import logging
from functools import wraps
from http import HTTPStatus

from flask import Blueprint
from flask import json, request, jsonify, Response

from openbrokerapi import errors
from openbrokerapi.response import *
from openbrokerapi.service_broker import *
from openbrokerapi.service_broker import ProvisionServiceState as PSS


class BrokerCredentials:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def get_blueprint(service_broker: ServiceBroker,
                  broker_credentials: BrokerCredentials,
                  logger: logging.Logger) -> Blueprint:
    """
    Returns the blueprint with service broker api.

    :param service_broker: Service broker used to handle requests
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
        services = service_broker.catalog()
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
            result = service_broker.provision(instance_id, provision_details, accepts_incomplete)
        except errors.ErrInstanceAlreadyExists as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrAsyncRequired as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.state == PSS.IS_ASYNC:
            return to_json_response(ProvisioningResponse(result.dashboard_url, result.operation)), HTTPStatus.ACCEPTED
        elif result.state == PSS.IDENTICAL_ALREADY_EXISTS:
            return to_json_response(ProvisioningResponse(result.dashboard_url, result.operation)), HTTPStatus.OK
        elif result.state == PSS.SUCCESSFUL_CREATED:
            return to_json_response(ProvisioningResponse(result.dashboard_url, result.operation)), HTTPStatus.CREATED
        else:
            raise errors.ServiceExeption('IllegalState, ServiceProvisioningState unknown.')

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
            result = service_broker.update(instance_id, update_details, accepts_incomplete)
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
            result = service_broker.bind(instance_id, binding_id, binding_details)
        except errors.ErrBindingAlreadyExists as e:
            logger.exception(e)
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrAppGuidNotProvided as e:
            logger.exception(e)
            return to_json_response(ErrorResponse(
                error="RequiresApp",
                description="This service supports generation of credentials through binding an application only."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        return to_json_response(result), HTTPStatus.CREATED

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
            service_broker.unbind(instance_id, binding_id, unbind_details)
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
            result = service_broker.deprovision(instance_id, deprovision_details, accepts_incomplete)
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
        result = service_broker.last_operation(instance_id, operation_data)

        return to_json_response(LastOperationResponse(result.state, result.description)), HTTPStatus.OK

    return openbroker


def serve(service_broker: ServiceBroker,
          credentials: BrokerCredentials,
          logger: logging.Logger = logging.root,
          port=5000,
          debug=False):
    """
    Starts flask with the given broker

    :param service_broker: Service broker used to handle requests
    :param credentials: Username and password that will be required to communicate with service broker
    :param logger: Used for api logs. This will not influence Flasks logging behavior
    :param port: Port
    :param debug: Enables debugging in flask app
    """

    from flask import Flask
    app = Flask(__name__)

    blueprint = get_blueprint(service_broker, credentials, logger)

    logger.debug("Register openbrokerapi blueprint")
    app.register_blueprint(blueprint)

    logger.info("Start Flask on 0.0.0.0:%s" % port)
    app.run('0.0.0.0', port, debug)
