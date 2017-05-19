from http import HTTPStatus

import jsonpickle
from flask import Flask, json, request, Response, jsonify
from werkzeug.exceptions import *

from cfbrokerapi import errors
from cfbrokerapi.response import ProvisioningResponse, DeprovisionResponse
from cfbrokerapi.service_broker import ServiceBroker, ProvisionDetails, DeprovisionDetails


def _create_app(service_broker):
    app = Flask(__name__)

    def versiontuple(v):
        return tuple(map(int, (v.split("."))))

    min_version = versiontuple("2.0")

    def print_request():
        print("--- Request -------------------------------")
        print("--- header")
        for k, v in request.headers:
            print(k, ":", v)
        print("--- body")
        print(request.data)
        print("-------------------------------")

    def check_version():
        version = request.headers.get("X-Broker-Api-Version", None)
        if not version:
            return BadRequest()
        if min_version > versiontuple(version):
            return PreconditionFailed()

    app.before_request(print_request)
    app.before_request(check_version)

    @app.route("/v2/catalog", methods=['GET'])
    def catalog():
        """
        :return: Catalog of broker (List of services) 
        """
        services = service_broker.catalog()
        return Response(
            jsonpickle.dumps({'services': services}, unpicklable=False),
            mimetype='application/json'
        )

    @app.route("/v2/service_instances/<instance_id>", methods=['PUT'])
    def provision(instance_id):
        """
        -> accepts_incomplete: boolean (support async)
        -> body: ProvisionDetails

        :param instance_id:
        return:

        * 201 Created
        * 200 OK - Already exists like it should be
        * 202 Accepted - async/poll
        * 409 Conflict - already exists (body:{})
        * 422 - Just async supported
        """

        try:
            details = json.loads(request.data)
            provision_details: ProvisionDetails = ProvisionDetails(**details)
        except TypeError as e:
            return BadRequest(str(e))

        try:
            result, http_code = service_broker.provision(instance_id, provision_details, False)
        except errors.ErrInstanceAlreadyExists:
            return jsonify(), HTTPStatus.CONFLICT
        except errors.ErrAsyncRequired:
            return jsonify(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            ), HTTPStatus.UNPROCESSABLE_ENTITY

        return Response(
            jsonpickle.dumps(ProvisioningResponse(result.dashboard_url, result.operation), unpicklable=False),
            mimetype='application/json',
            status=http_code
        )

    # @app.route("/v2/service_instances/<instance_id>", methods=['PATCH'])
    # def update(instance_id):
    #     """
    #     """
    #     return

    @app.route("/v2/service_instances/<instance_id>", methods=['DELETE'])
    def deprovision(instance_id):
        """
        -> service_id: string
        -> plan_id -> string
        -> accepts_incomplete= True\False

        :param instance_id:
        return:
        * 200 OK
        * 202 Accepted - async/poll
        * 410 Gone - if not exists (body: {})
        * 422 - Just async supported
        """
        try:

            plan_id = request.args["plan_id"]
            service_id = request.args["service_id"]
            # accepts_incomplete = request.args.get["accepts_incomplete", False]

            deprovision_details = DeprovisionDetails(plan_id, service_id)

        except KeyError as e:
            return BadRequest(str(e))

        try:
            result = service_broker.deprovision(instance_id, deprovision_details, False)
        except errors.ErrInstanceDoesNotExist:
            return jsonify(), 410
        except errors.ErrAsyncRequired:
            return jsonify(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations."
            ), 422

        if result.is_async:
            return Response(
                jsonpickle.dumps(DeprovisionResponse(result.operation), unpicklable=False),
                mimetype='application/json',
                status=202
            )
        else:
            return jsonify({}), 200

    return app


def serve(service_broker: ServiceBroker, port=5000):
    _create_app(service_broker).run('0.0.0.0', port, True)
