import base64
import http
import json
from unittest.mock import Mock

from flask_testing import TestCase
from werkzeug.wrappers import Response

from cfbrokerapi import _create_app, errors, BrokerCredentials
from cfbrokerapi.service_broker import Binding, ServiceBroker

expected_credentials = {"uri": "mysql://mysqluser:pass@mysqlhost:3306/dbname",
                        "username": "mysqluser",
                        "password": "pass",
                        "host": "mysqlhost",
                        "port": 3306,
                        "database": "dbname"}


class BindingTest(TestCase):
    auth_header = 'Basic ' + base64.b64encode(b":").decode("ascii")

    def create_app(self):
        self.broker: ServiceBroker = Mock()

        app = _create_app(self.broker, BrokerCredentials("", ""))
        return app

    def test_returns_200_if_binding_has_been_created(self):
        self.broker.bind.return_value = Binding(
            credentials=expected_credentials
        )

        response: Response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {
                    "app_guid": "app-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.CREATED)
        self.assertEquals(response.json, dict({
            "credentials": expected_credentials
        }))

    def test_returns_409_if_binding_already_exists(self):
        self.broker.bind.side_effect = errors.ErrBindingAlreadyExists()

        response: Response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {
                    "app_guid": "app-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.CONFLICT)
        self.assertEquals(response.json, dict())

    def test_returns_422_if_app_guid_is_required_but_not_given(self):
        self.broker.bind.side_effect = errors.ErrAppGuidNotProvided()

        response: Response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {}
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEquals(response.json, dict(
            error="RequiresApp",
            description="This service supports generation of credentials through binding an application only."
        ))

    def test_returns_401_if_request_not_contain_auth_header(self):
        response: Response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({}),
            headers={
                'X-Broker-Api-Version': '2.00'
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNAUTHORIZED)
