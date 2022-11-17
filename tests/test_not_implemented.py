import base64
import json
import logging

from flask import Flask

from openbrokerapi.auth import BrokerCredentials
from openbrokerapi.log_util import basic_config
from openbrokerapi.service_broker import ServiceBroker
from tests import BrokerTestCase


class NotImplementedBrokerTest(BrokerTestCase):
    auth_header = "Basic " + base64.b64encode(b":").decode("ascii")

    def create_app(self):
        from openbrokerapi.api import get_blueprint

        app = Flask(__name__)
        self.broker = ServiceBroker()

        app.register_blueprint(
            get_blueprint(
                self.broker, BrokerCredentials("", ""), basic_config(level=logging.WARN)
            )
        )
        return app

    def test_catalog_called_with_the_right_values(self):
        response = self.client.get(
            "/v2/catalog",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assert_status(response, 501)

    def test_provisioning_called_with_the_right_values(self):
        self.broker.service_id = lambda *_: "service-guid-here"

        response = self.client.put(
            "/v2/service_instances/here-instance-id?accepts_incomplete=true",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "organization_guid": "org-guid-here",
                    "space_guid": "space-guid-here",
                    "parameters": {"parameter1": 1},
                    "context": {
                        "organization_guid": "org-guid-here",
                        "space_guid": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assert_status(response, 501)

    def test_deprovisioning_is_called_with_the_right_values(self):
        self.broker.service_id = lambda *_: "service-guid-here"

        response = self.client.delete(
            "/v2/service_instances/here_instance_id?service_id=service-guid-here&plan_id=plan-id-here&accepts_incomplete=true",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assert_status(response, 501)

    def test_bind_called_with_the_right_values(self):
        self.broker.service_id = lambda *_: "service-guid-here"

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "bind_resource": {
                        "app_guid": "app-guid-here",
                        "route": "route-here",
                    },
                    "parameters": {"parameter1": 1},
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assert_status(response, 501)

    def test_unbind_is_called_with_the_right_values(self):
        self.broker.service_id = lambda *_: "service-guid-here"

        query = "service_id=service-guid-here&plan_id=plan-id-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s"
            % query,
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assert_status(response, 501)

    def test_update_called_with_the_right_values(self):
        self.broker.service_id = lambda *_: "service-guid-here"

        response = self.client.patch(
            "/v2/service_instances/here-service-instance-id?accepts_incomplete=true",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "parameters": {"parameter1": 1},
                    "previous_values": {
                        "plan_id": "old-plan-guid-here",
                        "service_id": "service-guid-here",
                        "organization_id": "org-guid-here",
                        "space_id": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assert_status(response, 501)
