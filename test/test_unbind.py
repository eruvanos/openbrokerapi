import base64
import http
from unittest.mock import Mock

from flask_testing import TestCase
from werkzeug.wrappers import Response

from openbrokerapi import _create_app, errors, BrokerCredentials
from openbrokerapi.service_broker import ServiceBroker


class BindingTest(TestCase):
    auth_header = 'Basic ' + base64.b64encode(b":").decode("ascii")

    def create_app(self):
        self.broker: ServiceBroker = Mock()

        app = _create_app(self.broker, BrokerCredentials("",""))
        return app

    def test_returns_200_if_binding_has_been_created(self):
        self.broker.unbind.return_value = None

        query = "service_id=service-id-here&plan_id=plan-id-here"
        response: Response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.OK)
        self.assertEquals(response.json, dict())

    def test_returns_410_if_binding_does_not_exists(self):
        self.broker.unbind.side_effect = errors.ErrBindingDoesNotExist()

        query = "service_id=service-id-here&plan_id=plan-id-here"
        response: Response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.GONE)
        self.assertEquals(response.json, dict())

    def test_returns_400_if_request_not_contain_auth_header(self):
        query = "service_id=service-id-here&plan_id=plan-id-here"
        response: Response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.00',
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNAUTHORIZED)
