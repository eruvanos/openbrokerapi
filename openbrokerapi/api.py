import logging
from typing import List
from functools import wraps
from http import HTTPStatus

from flask import Blueprint
from flask import json, request, jsonify, Response

from openbrokerapi import errors
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
    ProvisionedServiceSpec,
    Service,
    UnbindDetails,
    UpdateDetails,
)


class BrokerCredentials:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def get_blueprint(services: List[Service],
                  broker_credentials: BrokerCredentials,
                  logger: logging.Logger) -> Blueprint:
    """
    Returns the blueprint with service broker api.

    :param services: Services that this broker exposes
    :param broker_credentials: Username and password that will be required to communicate with service broker
    :param logger: Used for api logs. This will not influence Flasks logging behavior.
    :return: Blueprint to register with Flask app instance
    """
    openbroker = Blueprint('open_broker', __name__)

    def version_tuple(v):
        return tuple(map(int, (v.split("."))))

    min_version = version_tuple("2.13")

    def check_version():
        version = request.headers.get("X-Broker-Api-Version", None)
        if not version:
            return to_json_response(ErrorResponse(description="No X-Broker-Api-Version found.")), HTTPStatus.BAD_REQUEST
        if min_version > version_tuple(version):
            return to_json_response(ErrorResponse(
                description="Service broker requires version %d.%d+." % min_version)
            ), HTTPStatus.PRECONDITION_FAILED

    logger.debug("Apply check_version filter for version %s" % str(min_version))
    openbroker.before_request(check_version)

    def check_auth(username, password):
        return username == broker_credentials.username and password == broker_credentials.password

    def authenticate():
        """Sends a 401 response that enables basic auth"""
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', HTTPStatus.UNAUTHORIZED,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
            return f(*args, **kwargs)

        return decorated

    def get_service_by_id(service_id: str):
        for service in services:
            if service.id == service_id:
                return service
        raise KeyError('service {} not found'.format(service_id))

    def add_service_id_to_async_response(response, service_id: str):
        patch = False
        if isinstance(response, ProvisionedServiceSpec):
            if response.state == ProvisionState.IS_ASYNC:
                patch = True
        elif response.is_async:
            patch = True
        if patch:
            if response.operation is None:
                response.operation = service_id
            else:
                response.operation = ' '.join((service_id, response.operation))

    def print_request():
        logger.debug("--- Request Start -------------------")
        logger.debug("--- Header")
        for k, v in request.headers:
            logger.debug("%s:%s", k, v)
        logger.debug("--- Body")
        logger.debug(request.data)
        logger.debug("--- Request End ---------------------")

    openbroker.before_request(print_request)

    # Following https://stackoverflow.com/a/1118038
    def todict(obj):
        if isinstance(obj, dict):
            data = {}
            for (k, v) in obj.items():
                data[k] = todict(v)
            return data
        elif hasattr(obj, "__iter__") and not isinstance(obj, str):
            return [todict(v) for v in obj]
        elif hasattr(obj, "__dict__"):
            data = dict([(key, todict(value))
                         for key, value in obj.__dict__.items()
                         if not callable(value) and not key.startswith('_') and value is not None])
            return data
        else:
            return obj

    def to_json_response(obj):
        return jsonify(todict(obj))

    @openbroker.errorhandler(Exception)
    def error_handler(e):
        logger.exception(e)
        return to_json_response(ErrorResponse(
            description=str(e)
        )), HTTPStatus.INTERNAL_SERVER_ERROR

    @openbroker.route("/v2/catalog", methods=['GET'])
    @requires_auth
    def catalog():
        """
        :return: Catalog of broker (List of services)
        """
        return to_json_response(CatalogResponse(services))

    @openbroker.route("/v2/service_instances/<instance_id>", methods=['PUT'])
    @requires_auth
    def provision(instance_id):
        try:
            accepts_incomplete = 'true' == request.args.get("accepts_incomplete", 'false')

            details = json.loads(request.data)
            provision_details = ProvisionDetails(**details)
        except TypeError as e:
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            service = get_service_by_id(provision_details.service_id)
            result = service.provision(instance_id, provision_details, accepts_incomplete)
            add_service_id_to_async_response(result, service.id)
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
            raise errors.ServiceExeption('IllegalState, ProvisioningState unknown.')

    @openbroker.route("/v2/service_instances/<instance_id>", methods=['PATCH'])
    @requires_auth
    def update(instance_id):
        try:
            details = json.loads(request.data)
            update_details = UpdateDetails(**details)

            accepts_incomplete = 'true' == request.args.get("accepts_incomplete", 'false')
        except TypeError as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            service = get_service_by_id(update_details.service_id)
            result = service.update(instance_id, update_details, accepts_incomplete)
            add_service_id_to_async_response(result, service.id)
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
    @requires_auth
    def bind(instance_id, binding_id):
        try:
            details = json.loads(request.data)
            binding_details = BindDetails(**details)
        except KeyError as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            service = get_service_by_id(binding_details.service_id)
            result = service.bind(instance_id, binding_id, binding_details)
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
            raise errors.ServiceExeption('IllegalState, BindState unknown.')

    @openbroker.route("/v2/service_instances/<instance_id>/service_bindings/<binding_id>", methods=['DELETE'])
    @requires_auth
    def unbind(instance_id, binding_id):
        try:
            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            unbind_details = UnbindDetails(plan_id, service_id)
        except KeyError as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            service = get_service_by_id(unbind_details.service_id)
            service.unbind(instance_id, binding_id, unbind_details)
        except errors.ErrBindingDoesNotExist as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.GONE

        return to_json_response(EmptyResponse()), HTTPStatus.OK

    @openbroker.route("/v2/service_instances/<instance_id>", methods=['DELETE'])
    @requires_auth
    def deprovision(instance_id):
        try:
            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            accepts_incomplete = 'true' == request.args.get("accepts_incomplete", 'false')

            deprovision_details = DeprovisionDetails(plan_id, service_id)

        except KeyError as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(description=str(e))), HTTPStatus.BAD_REQUEST

        try:
            service = get_service_by_id(deprovision_details.service_id)
            result = service.deprovision(instance_id, deprovision_details, accepts_incomplete)
            add_service_id_to_async_response(result, service.id)
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
    @requires_auth
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
        service = get_service_by_id(service_id)
        result = service.last_operation(instance_id, operation_data)

        return to_json_response(LastOperationResponse(result.state, result.description)), HTTPStatus.OK

    return openbroker


def serve(services: List[Service],
          credentials: BrokerCredentials,
          logger: logging.Logger = logging.root,
          port=5000,
          debug=False):
    """
    Starts flask with the given broker

    :param services: Services that this broker provides
    :param credentials: Username and password that will be required to communicate with service broker
    :param logger: Used for api logs. This will not influence Flasks logging behavior
    :param port: Port
    :param debug: Enables debugging in flask app
    """

    from flask import Flask
    app = Flask(__name__)

    blueprint = get_blueprint(services, credentials, logger)

    logger.debug("Register openbrokerapi blueprint")
    app.register_blueprint(blueprint)

    logger.info("Start Flask on 0.0.0.0:%s" % port)
    app.run('0.0.0.0', port, debug)
