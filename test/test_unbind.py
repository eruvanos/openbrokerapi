import http

from test import BrokerTestCase
from openbrokerapi import errors
from openbrokerapi.service_broker import UnbindDetails


class UnbindTest(BrokerTestCase):

    def test_unbind_is_called_with_the_right_values(self):
        self.broker.unbind.return_value = None

        query = "service_id=service-id-here&plan_id=plan-id-here"
        self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_binding_id, actual_details = self.broker.unbind.call_args[0]
        self.assertEqual(actual_instance_id, "here_instance_id")
        self.assertEqual(actual_binding_id, "here_binding_id")

        self.assertIsInstance(actual_details, UnbindDetails)
        self.assertEqual(actual_details.plan_id, "plan-id-here")
        self.assertEqual(actual_details.service_id, "service-id-here")

    def test_returns_200_if_binding_has_been_created(self):
        self.broker.unbind.return_value = None

        query = "service_id=service-id-here&plan_id=plan-id-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json, dict())

    def test_returns_410_if_binding_does_not_exists(self):
        self.broker.unbind.side_effect = errors.ErrBindingDoesNotExist()

        query = "service_id=service-id-here&plan_id=plan-id-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.GONE)
        self.assertEqual(response.json, dict())

    def test_returns_400_if_request_not_contain_auth_header(self):
        query = "service_id=service-id-here&plan_id=plan-id-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.13',
            })

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)
