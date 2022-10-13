import logging
import warnings
from http import HTTPStatus
from json.decoder import JSONDecodeError
from typing import List, Union

from flask import Blueprint, Request
from flask import json, request

from openbrokerapi import errors, constants
from openbrokerapi.helper import to_json_response, ensure_list
from openbrokerapi.request_filter import (
    print_request,
    check_originating_identity,
    get_auth_filter,
    check_version,
    requires_application_json,
)
from openbrokerapi.response import (
    BindResponse,
    CatalogResponse,
    DeprovisionResponse,
    EmptyResponse,
    ErrorResponse,
    LastOperationResponse,
    ProvisioningResponse,
    UpdateResponse,
    UnbindResponse,
    GetInstanceResponse,
    GetBindingResponse,
)
from openbrokerapi.router import Router
from openbrokerapi.service_broker import (
    BindDetails,
    BindState,
    DeprovisionDetails,
    ProvisionDetails,
    ProvisionState,
    UnbindDetails,
    UpdateDetails,
    ServiceBroker,
    OperationState,
)
from openbrokerapi.settings import MIN_VERSION, DISABLE_VERSION_CHECK


class BrokerCredentials:
    """
    Credentials, which will be used to validate authenticate requests
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def _check_plan_id(broker: ServiceBroker, plan_id) -> bool:
    """
    Checks that the plan_id exists in the catalog
    :return: boolean
    """
    for service in ensure_list(broker.catalog()):
        for plan in service.plans:
            if plan.id == plan_id:
                return True
    return False


def get_blueprint(
    service_broker: ServiceBroker,
    broker_credentials: Union[None, List[BrokerCredentials], BrokerCredentials],
    logger: logging.Logger,
) -> Blueprint:
    """
    Returns the blueprint with service broker api.

    :param service_broker: Services that this broker exposes
    :param broker_credentials: Optional Usernames and passwords that will be required to communicate with service broker
    :param logger: Used for api logs. This will not influence Flasks logging behavior.
    :return: Blueprint to register with Flask app instance
    """
    openbroker = Blueprint("open_broker", __name__)

    # Apply filters
    logger.debug("Apply print_request filter for debugging")
    openbroker.before_request(print_request)

    if DISABLE_VERSION_CHECK:
        logger.warning(
            "Minimum API version is not checked, this can cause illegal contracts between service broker and platform!"
        )
    else:
        logger.debug("Apply check_version filter for version %s" % str(MIN_VERSION))
        openbroker.before_request(check_version)

    logger.debug("Apply check_originating_identity filter")
    openbroker.before_request(check_originating_identity)

    if broker_credentials is not None:
        broker_credentials = ensure_list(broker_credentials)
        logger.debug(
            "Apply check_auth filter with {} credentials".format(
                len(broker_credentials)
            )
        )
        openbroker.before_request(get_auth_filter(broker_credentials))

    def extract_authorization_username(request: Request):
        if request.authorization is not None:
            return request.authorization.username
        else:
            return None

    @openbroker.errorhandler(Exception)
    def error_handler(e):
        logger.exception(e)
        return (
            to_json_response(
                ErrorResponse(description=constants.DEFAULT_EXCEPTION_ERROR_MESSAGE)
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @openbroker.errorhandler(NotImplementedError)
    def error_handler_not_implemented(e):
        logger.exception(e)
        return (
            to_json_response(
                ErrorResponse(
                    description=constants.DEFAULT_NOT_IMPLEMENTED_ERROR_MESSAGE
                )
            ),
            HTTPStatus.NOT_IMPLEMENTED,
        )

    @openbroker.errorhandler(errors.ErrBadRequest)
    def error_handler_bad_request(e):
        logger.exception(e)
        return (
            to_json_response(
                ErrorResponse(description=constants.DEFAULT_BAD_REQUEST_ERROR_MESSAGE)
            ),
            HTTPStatus.BAD_REQUEST,
        )

    @openbroker.route("/v2/catalog", methods=["GET"])
    def catalog():
        """
        :return: Catalog of broker (List of services)
        """
        catalog = ensure_list(service_broker.catalog())
        return to_json_response(CatalogResponse(list(catalog)))

    @openbroker.route("/v2/service_instances/<instance_id>", methods=["PUT"])
    @requires_application_json
    def provision(instance_id):
        try:
            accepts_incomplete = "true" == request.args.get(
                "accepts_incomplete", "false"
            )

            provision_details = ProvisionDetails(**json.loads(request.data))
            provision_details.originating_identity = request.originating_identity
            provision_details.authorization_username = extract_authorization_username(
                request
            )

            if not _check_plan_id(service_broker, provision_details.plan_id):
                raise TypeError("plan_id not found in this service.")
        except (TypeError, KeyError, JSONDecodeError) as e:
            logger.exception(e)
            return (
                to_json_response(ErrorResponse(description=str(e))),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            result = service_broker.provision(
                instance_id=instance_id,
                details=provision_details,
                async_allowed=accepts_incomplete
            )
            if result is None:
                warnings.warn("Provision has to return ProvisionedServiceSpec")
                raise errors.ServiceException("Internal broker error")

        except errors.ErrInstanceAlreadyExists as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrInvalidParameters as e:
            return (
                to_json_response(ErrorResponse("InvalidParameters", str(e))),
                HTTPStatus.BAD_REQUEST,
            )
        except errors.ErrAsyncRequired as e:
            logger.exception(e)
            return (
                to_json_response(
                    ErrorResponse(
                        error="AsyncRequired",
                        description="This service plan requires client support for asynchronous service operations.",
                    )
                ),
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )

        if result.state == ProvisionState.IS_ASYNC:
            return (
                to_json_response(
                    ProvisioningResponse(result.dashboard_url, result.operation)
                ),
                HTTPStatus.ACCEPTED,
            )
        elif result.state == ProvisionState.IDENTICAL_ALREADY_EXISTS:
            return (
                to_json_response(
                    ProvisioningResponse(result.dashboard_url, result.operation)
                ),
                HTTPStatus.OK,
            )
        elif result.state == ProvisionState.SUCCESSFUL_CREATED:
            return (
                to_json_response(
                    ProvisioningResponse(result.dashboard_url, result.operation)
                ),
                HTTPStatus.CREATED,
            )
        else:
            raise errors.ServiceException("IllegalState, ProvisioningState unknown.")

    @openbroker.route("/v2/service_instances/<instance_id>", methods=["PATCH"])
    @requires_application_json
    def update(instance_id):
        try:
            accepts_incomplete = "true" == request.args.get(
                "accepts_incomplete", "false"
            )

            update_details = UpdateDetails(**json.loads(request.data))
            update_details.originating_identity = request.originating_identity
            update_details.authorization_username = extract_authorization_username(
                request
            )
            plan_id = update_details.plan_id
            if plan_id and not _check_plan_id(service_broker, plan_id):
                raise TypeError("plan_id not found in this service.")
        except (TypeError, KeyError, JSONDecodeError) as e:
            logger.exception(e)
            return (
                to_json_response(ErrorResponse(description=str(e))),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            result = service_broker.update(
                instance_id=instance_id,
                details=update_details,
                async_allowed=accepts_incomplete
            )
            if result is None:
                warnings.warn("Update has to return UpdateServiceSpec")
                raise errors.ServiceException("Internal broker error")
        except errors.ErrInvalidParameters as e:
            return (
                to_json_response(ErrorResponse("InvalidParameters", str(e))),
                HTTPStatus.BAD_REQUEST,
            )
        except errors.ErrAsyncRequired as e:
            logger.exception(e)
            return (
                to_json_response(
                    ErrorResponse(
                        error="AsyncRequired",
                        description="This service plan requires client support for asynchronous service operations.",
                    )
                ),
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        except errors.ErrConcurrentInstanceAccess as e:
            logger.exception(e)
            error_response = ErrorResponse(
                error="ConcurrencyError",
                description="The Service Broker does not support concurrent requests that mutate the same resource.",
            )
            return to_json_response(error_response), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.is_async:
            return (
                to_json_response(
                    UpdateResponse(result.operation, result.dashboard_url)
                ),
                HTTPStatus.ACCEPTED,
            )
        else:
            return (
                to_json_response(UpdateResponse(None, result.dashboard_url)),
                HTTPStatus.OK,
            )

    @openbroker.route(
        "/v2/service_instances/<instance_id>/service_bindings/<binding_id>",
        methods=["PUT"],
    )
    @requires_application_json
    def bind(instance_id, binding_id):
        try:
            accepts_incomplete = "true" == request.args.get(
                "accepts_incomplete", "false"
            )

            binding_details = BindDetails(**json.loads(request.data))
            binding_details.originating_identity = request.originating_identity
            binding_details.authorization_username = extract_authorization_username(
                request
            )
            if not _check_plan_id(service_broker, binding_details.plan_id):
                raise TypeError("plan_id not found in this service.")
        except (TypeError, KeyError, JSONDecodeError) as e:
            logger.exception(e)
            return (
                to_json_response(ErrorResponse(description=str(e))),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            result = service_broker.bind(
                instance_id=instance_id,
                binding_id=binding_id,
                details=binding_details,
                async_allowed=accepts_incomplete
            )
            if result is None:
                warnings.warn("Bind has to return a Binding")
                raise errors.ServiceException("Internal broker error")
        except errors.ErrBindingAlreadyExists as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrAppGuidNotProvided as e:
            logger.exception(e)
            return (
                to_json_response(
                    ErrorResponse(
                        error="RequiresApp",
                        description="This service supports generation of credentials through binding an application only.",
                    )
                ),
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        except errors.ErrConcurrentInstanceAccess as e:
            logger.exception(e)
            error_response = ErrorResponse(
                error="ConcurrencyError",
                description="The Service Broker does not support concurrent requests that mutate the same resource.",
            )
            return to_json_response(error_response), HTTPStatus.UNPROCESSABLE_ENTITY

        response = BindResponse(
            credentials=result.credentials,
            syslog_drain_url=result.syslog_drain_url,
            route_service_url=result.route_service_url,
            volume_mounts=result.volume_mounts,
        )
        if result.state == BindState.SUCCESSFUL_BOUND:
            return to_json_response(response), HTTPStatus.CREATED
        elif result.state == BindState.IDENTICAL_ALREADY_EXISTS:
            return to_json_response(response), HTTPStatus.OK
        elif result.state == BindState.IS_ASYNC:
            return (
                to_json_response(BindResponse(operation=result.operation)),
                HTTPStatus.ACCEPTED,
            )
        else:
            raise errors.ServiceException("IllegalState, BindState unknown.")

    @openbroker.route(
        "/v2/service_instances/<instance_id>/service_bindings/<binding_id>",
        methods=["DELETE"],
    )
    def unbind(instance_id, binding_id):
        try:
            accepts_incomplete = "true" == request.args.get(
                "accepts_incomplete", "false"
            )

            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]

            unbind_details = UnbindDetails(service_id=service_id, plan_id=plan_id)
            unbind_details.originating_identity = request.originating_identity
            unbind_details.authorization_username = extract_authorization_username(
                request
            )
            if not _check_plan_id(service_broker, unbind_details.plan_id):
                raise TypeError("plan_id not found in this service.")
        except (TypeError, KeyError) as e:
            logger.exception(e)
            return (
                to_json_response(ErrorResponse(description=str(e))),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            result = service_broker.unbind(
                instance_id=instance_id,
                binding_id=binding_id,
                details=unbind_details,
                async_allowed=accepts_incomplete
            )
            if result is None:
                warnings.warn("Unbind has to return a UnbindSpec")
                raise errors.ServiceException("Internal broker error")
        except errors.ErrBindingDoesNotExist as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.GONE
        except errors.ErrConcurrentInstanceAccess as e:
            logger.exception(e)
            error_response = ErrorResponse(
                error="ConcurrencyError",
                description="The Service Broker does not support concurrent requests that mutate the same resource.",
            )
            return to_json_response(error_response), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.is_async:
            return (
                to_json_response(UnbindResponse(result.operation)),
                HTTPStatus.ACCEPTED,
            )
        else:
            return to_json_response(EmptyResponse()), HTTPStatus.OK

    @openbroker.route("/v2/service_instances/<instance_id>", methods=["DELETE"])
    def deprovision(instance_id):
        try:
            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            accepts_incomplete = "true" == request.args.get(
                "accepts_incomplete", "false"
            )

            deprovision_details = DeprovisionDetails(
                service_id=service_id, plan_id=plan_id
            )
            deprovision_details.originating_identity = request.originating_identity
            deprovision_details.authorization_username = extract_authorization_username(
                request
            )
            if not _check_plan_id(service_broker, deprovision_details.plan_id):
                raise TypeError("plan_id not found in this service.")
        except (TypeError, KeyError) as e:
            logger.exception(e)
            return (
                to_json_response(ErrorResponse(description=str(e))),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            result = service_broker.deprovision(
                instance_id=instance_id,
                details=deprovision_details,
                async_allowed=accepts_incomplete
            )
            if result is None:
                warnings.warn("Deprovision has to return a DeprovisionServiceSpec")
                raise errors.ServiceException("Internal broker error")
        except errors.ErrInstanceDoesNotExist as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.GONE
        except errors.ErrAsyncRequired as e:
            logger.exception(e)
            return (
                to_json_response(
                    ErrorResponse(
                        error="AsyncRequired",
                        description="This service plan requires client support for asynchronous service operations.",
                    )
                ),
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        except errors.ErrConcurrentInstanceAccess as e:
            logger.exception(e)
            error_response = ErrorResponse(
                error="ConcurrencyError",
                description="The Service Broker does not support concurrent requests that mutate the same resource.",
            )
            return to_json_response(error_response), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.is_async:
            return (
                to_json_response(DeprovisionResponse(result.operation)),
                HTTPStatus.ACCEPTED,
            )
        else:
            return to_json_response(EmptyResponse()), HTTPStatus.OK

    @openbroker.route(
        "/v2/service_instances/<instance_id>/last_operation", methods=["GET"]
    )
    def last_operation(instance_id):
        service_id = request.args.get("service_id", None)
        plan_id = request.args.get("plan_id", None)

        operation_data = request.args.get("operation", None)

        try:
            result = service_broker.last_operation(
                instance_id=instance_id,
                operation_data=operation_data,
                service_id=service_id, plan_id=plan_id
            )
            if result is None:
                warnings.warn("Last Operation has to return a LastOperation")
                raise errors.ServiceException("Internal broker error")
            return (
                to_json_response(
                    LastOperationResponse(result.state, result.description)
                ),
                HTTPStatus.OK,
            )
        except errors.ErrInstanceDoesNotExist:
            return (
                to_json_response(LastOperationResponse(OperationState.SUCCEEDED, "")),
                HTTPStatus.GONE,
            )

    @openbroker.route(
        "/v2/service_instances/<instance_id>/service_bindings/<binding_id>/last_operation",
        methods=["GET"],
    )
    def last_binding_operation(instance_id, binding_id):
        service_id = request.args.get("service_id", None)
        plan_id = request.args.get("plan_id", None)

        operation_data = request.args.get("operation", None)
        result = service_broker.last_binding_operation(
            instance_id=instance_id,
            binding_id=binding_id,
            operation_data=operation_data,
            service_id=service_id,
            plan_id=plan_id,
        )
        if result is None:
            warnings.warn("Last Binding Operation has to return a LastOperation")
            raise errors.ServiceException("Internal broker error")
        return (
            to_json_response(LastOperationResponse(result.state, result.description)),
            HTTPStatus.OK,
        )

    @openbroker.route("/v2/service_instances/<instance_id>", methods=["GET"])
    def get_instance(instance_id):
        try:
            result = service_broker.get_instance(
                instance_id=instance_id
            )
            if result is None:
                warnings.warn("Get Instance has to return GetInstanceDetailsSpec")
                raise errors.ServiceException("Internal broker error")

            response = GetInstanceResponse(
                service_id=result.service_id,
                plan_id=result.plan_id,
                dashboard_url=result.dashboard_url,
                parameters=result.parameters,
            )
            return to_json_response(response), HTTPStatus.OK

        except errors.ErrInstanceDoesNotExist:
            return to_json_response(EmptyResponse()), HTTPStatus.NOT_FOUND
        except errors.ErrConcurrentInstanceAccess:
            error_response = ErrorResponse(
                error="ConcurrencyError",
                description="The Service Broker does not support concurrent requests that mutate the same resource.",
            )
            return to_json_response(error_response), HTTPStatus.UNPROCESSABLE_ENTITY

    @openbroker.route(
        "/v2/service_instances/<instance_id>/service_bindings/<binding_id>",
        methods=["GET"],
    )
    def get_binding(instance_id, binding_id):
        try:
            result = service_broker.get_binding(
                instance_id=instance_id,
                binding_id=binding_id
            )
            if result is None:
                warnings.warn("Get Binding has to return a GetBindingSpec")
                raise errors.ServiceException("Internal broker error")

            response = GetBindingResponse(
                credentials=result.credentials,
                syslog_drain_url=result.syslog_drain_url,
                route_service_url=result.route_service_url,
                volume_mounts=result.volume_mounts,
                parameters=result.parameters,
            )
            return to_json_response(response), HTTPStatus.OK
        except errors.ErrBindingDoesNotExist:
            return to_json_response(EmptyResponse()), HTTPStatus.NOT_FOUND

    return openbroker


def serve_multiple(
    service_brokers: List[ServiceBroker],
    credentials: Union[List[BrokerCredentials], BrokerCredentials, None],
    logger: logging.Logger = logging.root,
    host="0.0.0.0",
    port=5000,
    debug=False,
):
    router = Router(*service_brokers)
    serve(
        service_broker=router,
        credentials=credentials,
        logger=logger,
        host=host,
        port=port,
        debug=debug,
    )


def serve(
    service_broker: ServiceBroker,
    credentials: Union[List[BrokerCredentials], BrokerCredentials, None],
    logger: logging.Logger = logging.root,
    host="0.0.0.0",
    port=5000,
    debug=False,
):
    """
    Starts flask with the given brokers.
    You can provide a list or just one ServiceBroker

    :param service_broker: ServicesBroker for services to provide
    :param credentials: Username and password that will be required to communicate with service broker
    :param logger: Used for api logs. This will not influence Flasks logging behavior
    :param host: Host, defaults to all interfaces (0.0.0.0)
    :param port: Port
    :param debug: Enables debugging in flask app
    """

    from flask import Flask

    app = Flask(__name__)
    app.debug = debug

    blueprint = get_blueprint(service_broker, credentials, logger)

    logger.debug("Register openbrokerapi blueprint")
    app.register_blueprint(blueprint)

    try:
        from gevent.pywsgi import WSGIServer

        logger.info(f"Start Gevent server on {host}:{port}")
        http_server = WSGIServer((host, port), app)
        http_server.serve_forever()
    except ImportError:

        logger.info(f"Start Flask on {host}:{port}")
        logger.warning("Use a server like gevent or gunicorn for production!")
        app.run(host, port)
