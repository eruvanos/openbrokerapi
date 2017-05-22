from functools import wraps

from http import HTTPStatus

from flask import Flask, json, request, jsonify, Response
from werkzeug.exceptions import *

from . import errors
from .response import *
from .service_broker import *


class BrokerCredentials:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def _create_app(service_broker, broker_credentials, print_requests=False):
    app = Flask(__name__)

    def versiontuple(v):
        return tuple(map(int, (v.split("."))))

    def check_version():
        version = request.headers.get("X-Broker-Api-Version", None)
        if not version:
            return BadRequest()
        if min_version > versiontuple(version):
            return PreconditionFailed()

    min_version = versiontuple("2.0")
    app.before_request(check_version)

    def check_auth(username, password):
        return username == broker_credentials.username and password == broker_credentials.password

    def authenticate():
        """Sends a 401 response that enables basic auth"""
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return authenticate()
            return f(*args, **kwargs)

        return decorated

    if print_requests:
        def print_request():
            print("--- Request -------------------")
            print("--- header")
            for k, v in request.headers:
                print(k, ":", v)
            print("--- body")
            print(request.data)
            print("-------------------------------")

        app.before_request(print_request)

    def to_json_response(obj):
        return jsonify({k: v for k, v in obj.__dict__.items() if v is not None})

    @app.route("/v2/catalog", methods=['GET'])
    @requires_auth
    def catalog():
        """
        :return: Catalog of broker (List of services) 
        """
        services = service_broker.catalog()
        return to_json_response(CatalogResponse(services))

    @app.route("/v2/service_instances/<instance_id>", methods=['PUT'])
    @requires_auth
    def provision(instance_id):
        try:
            details = json.loads(request.data)
            provision_details: ProvisionDetails = ProvisionDetails(**details)
        except TypeError as e:
            return BadRequest(str(e))

        try:
            result = service_broker.provision(instance_id, provision_details, False)
        except errors.ErrInstanceAlreadyExists:
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrAsyncRequired:
            return to_json_response(ErrorResponse(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        return to_json_response(ProvisioningResponse(result.dashboard_url, result.operation)), HTTPStatus.CREATED

    @app.route("/v2/service_instances/<instance_id>", methods=['PATCH'])
    @requires_auth
    def update(instance_id):
        try:
            details = json.loads(request.data)
            update_details: UpdateDetails = UpdateDetails(**details)
        except TypeError as e:
            return BadRequest(str(e))

        try:
            result = service_broker.update(instance_id, update_details, False)
        except errors.ErrAsyncRequired:
            return to_json_response(ErrorResponse(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.is_async:
            return to_json_response(UpdateResponse(result.operation)), HTTPStatus.ACCEPTED
        else:
            return to_json_response(EmptyResponse()), HTTPStatus.OK

    @app.route("/v2/service_instances/<instance_id>/service_bindings/<binding_id>", methods=['PUT'])
    @requires_auth
    def bind(instance_id, binding_id):
        try:
            details = json.loads(request.data)
            binding_details: BindDetails = BindDetails(**details)
        except KeyError as e:
            return BadRequest(str(e))

        try:
            result = service_broker.bind(instance_id, binding_id, binding_details)
        except errors.ErrBindingAlreadyExists:
            return to_json_response(EmptyResponse()), HTTPStatus.CONFLICT
        except errors.ErrAppGuidNotProvided:
            return to_json_response(ErrorResponse(
                error="RequiresApp",
                description="This service supports generation of credentials through binding an application only."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        return to_json_response(result), HTTPStatus.CREATED

    @app.route("/v2/service_instances/<instance_id>/service_bindings/<binding_id>", methods=['DELETE'])
    @requires_auth
    def unbind(instance_id, binding_id):
        try:
            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            unbind_details: UnbindDetails = UnbindDetails(plan_id, service_id)
        except KeyError as e:
            return BadRequest(str(e))

        try:
            service_broker.unbind(instance_id, binding_id, unbind_details)
        except errors.ErrBindingDoesNotExist:
            return to_json_response(EmptyResponse()), HTTPStatus.GONE

        return to_json_response(EmptyResponse()), HTTPStatus.OK

    @app.route("/v2/service_instances/<instance_id>", methods=['DELETE'])
    @requires_auth
    def deprovision(instance_id):
        try:

            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            accepts_incomplete = request.args.get("accepts_incomplete", False)

            deprovision_details = DeprovisionDetails(plan_id, service_id)

        except KeyError as e:
            return BadRequest(str(e))

        try:
            result = service_broker.deprovision(instance_id, deprovision_details, accepts_incomplete)
        except errors.ErrInstanceDoesNotExist:
            return to_json_response(EmptyResponse()), HTTPStatus.GONE
        except errors.ErrAsyncRequired:
            return to_json_response(ErrorResponse(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            )), HTTPStatus.UNPROCESSABLE_ENTITY

        if result.is_async:
            return to_json_response(DeprovisionResponse(result.operation)), HTTPStatus.ACCEPTED
        else:
            return to_json_response(EmptyResponse()), HTTPStatus.OK

    return app


def serve(service_broker: ServiceBroker, credentials: BrokerCredentials, port=5000, print_requests=False):
    _create_app(service_broker, credentials, print_requests).run('0.0.0.0', port, True)
