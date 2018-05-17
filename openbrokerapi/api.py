import logging
from http import HTTPStatus
from typing import List, Union

from flask import Blueprint
from flask import json, request

from openbrokerapi import errors
from openbrokerapi.helper import to_json_response, ensure_list
from openbrokerapi.request_filter import print_request, check_originating_identity, get_auth_filter, check_version, \
    requires_application_json
from openbrokerapi.response import (
    BindResponse,
    CatalogResponse,
    DeprovisionResponse,
    EmptyResponse,
    ErrorResponse,
    LastOperationResponse,
    ProvisioningResponse,
    UpdateResponse,
)
from openbrokerapi.service_broker import (
    BindDetails,
    BindState,
    DeprovisionDetails,
    ProvisionDetails,
    ProvisionState,
    UnbindDetails,
    UpdateDetails,
    ServiceBroker)
from openbrokerapi.settings import MIN_VERSION


class BrokerCredentials:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def get_blueprint(service_brokers: Union[List[ServiceBroker], ServiceBroker],
                  broker_credentials: Union[None, List[BrokerCredentials], BrokerCredentials],
                  logger: logging.Logger) -> Blueprint:
    """
    Returns the blueprint with service broker api.

    :param service_brokers: Services that this broker exposes
    :param broker_credentials: Optional Usernames and passwords that will be required to communicate with service broker
    :param logger: Used for api logs. This will not influence Flasks logging behavior.
    :return: Blueprint to register with Flask app instance
    """
    openbroker = Blueprint('open_broker', __name__)
    service_brokers = ensure_list(service_brokers)

    # Apply filters
    logger.debug("Apply print_request filter for debugging")
    openbroker.before_request(print_request)

    logger.debug("Apply check_version filter for version %s" % str(MIN_VERSION))
    openbroker.before_request(check_version)

    logger.debug("Apply check_originating_identity filter")
    openbroker.before_request(check_originating_identity)

    if broker_credentials is not None:
        broker_credentials = ensure_list(broker_credentials)
        logger.debug("Apply check_auth filter with {} credentials".format(len(broker_credentials)))
        openbroker.before_request(get_auth_filter(broker_credentials))

    def get_broker_by_id(service_id: str):
        for service in service_brokers:
            if service.service_id() == service_id:
                return service
        raise KeyError('Service {} not found'.format(service_id))

    def add_service_id_to_async_response(response, service_id: str):
        if response.is_async:
            if response.operation is None:
                response.operation = service_id
            else:
                response.operation = ' '.join((service_id, response.operation))

    @openbroker.errorhandler(Exception)
    def error_handler(e):
        logger.exception(e)
        return to_json_response(ErrorResponse(
            description=str(e)
        )), HTTPStatus.INTERNAL_SERVER_ERROR

    @openbroker.route("/v2/catalog", methods=['GET'])
    def catalog():
        """
        :return: Catalog of broker (List of services)
        """
        return to_json_response(CatalogResponse(list(s.catalog() for s in service_brokers)))

    @openbroker.route("/v2/service_instances/<instance_id>", methods=['PUT'])
    @requires_application_json
    def provision(instance_id):
        try:
            accepts_incomplete = 'true' == request.args.get("accepts_incomplete", 'false')
            if not request.is_json:
                er = ErrorResponse(description='Improper Content-Type header. Expecting "application/json"')
                return to_json_response(er), HTTPStatus.BAD_REQUEST

            provision_details = ProvisionDetails(**json.loads(request.data))
            provision_details.originating_identity = request.originating_identity
            provision_details.authorization_username = request.authorization.username
            broker = get_broker_by_id(provision_details.service_id)
            if not broker.check_plan_id(provision_details.plan_id):
                raise TypeError('plan_id not found in this service.')
        except (TypeError, KeyError) as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            result = broker.provision(instance_id, provision_details, accepts_incomplete)
            add_service_id_to_async_response(result, broker.service_id())
        except errors.ErrInstanceAlreadyExists as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrAsyncRequired as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.state == ProvisionState.IS_ASYNC:
            return to_json_response(ProvisioningResponse(result.dashboard_url, result.operation)), HTTPStatus.ACCEPTED
        elif result.state == ProvisionState.IDENTICAL_ALREADY_EXISTS:
            return to_json_response(ProvisioningResponse(result.dashboard_url, result.operation)), HTTPStatus.OK
        elif result.state == ProvisionState.SUCCESSFUL_CREATED:
            return to_json_response(ProvisioningResponse(result.dashboard_url, result.operation)), HTTPStatus.CREATED
        else:
            raise errors.ServiceException('IllegalState, ProvisioningState unknown.')

    @openbroker.route("/v2/service_instances/<instance_id>", methods=['PATCH'])
    @requires_application_json
    def update(instance_id):
        try:
            accepts_incomplete = 'true' == request.args.get("accepts_incomplete", 'false')

            update_details = UpdateDetails(**json.loads(request.data))
            update_details.originating_identity = request.originating_identity
            update_details.authorization_username = request.authorization.username
            broker = get_broker_by_id(update_details.service_id)
            if not broker.check_plan_id(update_details.plan_id):
                raise TypeError('plan_id not found in this service.')
        except (TypeError, KeyError) as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            result = broker.update(instance_id, update_details, accepts_incomplete)
            add_service_id_to_async_response(result, broker.service_id())
        except errors.ErrAsyncRequired as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.is_async:
            return to_json_response(UpdateResponse(result.operation)), HTTPStatus.ACCEPTED
        else:
            return to_json_response(EmptyResponse()), HTTPStatus.OK

    @openbroker.route("/v2/service_instances/<instance_id>/service_bindings/<binding_id>", methods=['PUT'])
    @requires_application_json
    def bind(instance_id, binding_id):
        try:
            binding_details = BindDetails(**json.loads(request.data))
            binding_details.originating_identity = request.originating_identity
            binding_details.authorization_username = request.authorization.username
            broker = get_broker_by_id(binding_details.service_id)
            if not broker.check_plan_id(binding_details.plan_id):
                raise TypeError('plan_id not found in this service.')
        except (TypeError, KeyError) as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            result = broker.bind(instance_id, binding_id, binding_details)
        except errors.ErrBindingAlreadyExists as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrAppGuidNotProvided as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(
                error="RequiresApp",
                description="This service supports generation of credentials through binding an application only."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        response = BindResponse(
            credentials=result.credentials,
            syslog_drain_url=result.syslog_drain_url,
            route_service_url=result.route_service_url,
            volume_mounts=result.volume_mounts
        )
        if result.state == BindState.SUCCESSFUL_BOUND:
            return to_json_response(response), HTTPStatus.CREATED
        elif result.state == BindState.IDENTICAL_ALREADY_EXISTS:
            return to_json_response(response), HTTPStatus.OK
        else:
            raise errors.ServiceException('IllegalState, BindState unknown.')

    @openbroker.route("/v2/service_instances/<instance_id>/service_bindings/<binding_id>", methods=['DELETE'])
    def unbind(instance_id, binding_id):
        try:
            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            unbind_details = UnbindDetails(plan_id, service_id)
            unbind_details.originating_identity = request.originating_identity
            unbind_details.authorization_username = request.authorization.username
            broker = get_broker_by_id(unbind_details.service_id)
            if not broker.check_plan_id(unbind_details.plan_id):
                raise TypeError('plan_id not found in this service.')
        except (TypeError, KeyError) as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            broker.unbind(instance_id, binding_id, unbind_details)
        except errors.ErrBindingDoesNotExist as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.GONE

        return to_json_response(EmptyResponse()), HTTPStatus.OK

    @openbroker.route("/v2/service_instances/<instance_id>", methods=['DELETE'])
    def deprovision(instance_id):
        try:
            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            accepts_incomplete = 'true' == request.args.get("accepts_incomplete", 'false')

            deprovision_details = DeprovisionDetails(plan_id, service_id)
            deprovision_details.originating_identity = request.originating_identity
            deprovision_details.authorization_username = request.authorization.username
            broker = get_broker_by_id(deprovision_details.service_id)
            if not broker.check_plan_id(deprovision_details.plan_id):
                raise TypeError('plan_id not found in this service.')
        except (TypeError, KeyError) as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            result = broker.deprovision(instance_id, deprovision_details, accepts_incomplete)
            add_service_id_to_async_response(result, broker.service_id())
        except errors.ErrInstanceDoesNotExist as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.GONE
        except errors.ErrAsyncRequired as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.is_async:
            return to_json_response(DeprovisionResponse(result.operation)), HTTPStatus.ACCEPTED
        else:
            return to_json_response(EmptyResponse()), HTTPStatus.OK

    @openbroker.route("/v2/service_instances/<instance_id>/last_operation", methods=['GET'])
    def last_operation(instance_id):
        # Not required
        # service_id = request.args.get("service_id", None)
        # plan_id = request.args.get("plan_id", None)

        operation_data = request.args.get("operation", None)
        data = operation_data.split(' ', maxsplit=1)
        service_id = data[0]
        if len(data) == 2:
            operation_data = data[1]
        else:
            operation_data = None
        broker = get_broker_by_id(service_id)
        result = broker.last_operation(instance_id, operation_data)

        return to_json_response(LastOperationResponse(result.state, result.description)), HTTPStatus.OK

    return openbroker


def serve(service_brokers: Union[List[ServiceBroker], ServiceBroker],
          credentials: Union[List[BrokerCredentials], BrokerCredentials, None],
          logger: logging.Logger = logging.root,
          port=5000,
          debug=False):
    """
    Starts flask with the given brokers.
    You can provide a list or just one ServiceBroker

    :param service_brokers: ServicesBroker for services to provide
    :param credentials: Username and password that will be required to communicate with service broker
    :param logger: Used for api logs. This will not influence Flasks logging behavior
    :param port: Port
    :param debug: Enables debugging in flask app
    """

    from flask import Flask
    app = Flask(__name__)

    blueprint = get_blueprint(service_brokers, credentials, logger)

    logger.debug("Register openbrokerapi blueprint")
    app.register_blueprint(blueprint)

    logger.info("Start Flask on 0.0.0.0:%s" % port)
    app.run('0.0.0.0', port, debug)
