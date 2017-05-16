import jsonpickle
from flask import Flask, json, request, Response

from cfbrokerapi.service_broker import ServiceBroker


def serve(service_broker: ServiceBroker, port=5000):
    app = Flask(__name__)

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
        -> body: ServerProvisioningRequest
    
        :param instance_id:
        return:
        * 201 Created
        * 200 OK - Already exists like it should be
        * 202 Accepted - async/poll
        * 409 Conflict - already exists (body:{})
        * 422 - Just async supported
        """

        details = json.loads(request.json)

        result = service_broker.provision(instance_id, details, False)
        return result

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
        return

    app.run('0.0.0.0', port, True)

    ### Stuff




    if __name__ == "__main__":
        serve()
