import http

from openbrokerapi import errors
from test import BrokerTestCase


class PrecheckTest(BrokerTestCase):

    def setUp(self):
        self.broker.service_id.return_value = 'service-guid-here'

    def test_returns_401_if_request_not_contain_auth_header(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                'X-Broker-Api-Version': '2.13',
            })

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_returns_412_if_version_is_not_supported(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                'X-Broker-Api-Version': '2.9',
            })

        self.assertEqual(response.status_code, http.HTTPStatus.PRECONDITION_FAILED)
        self.assertEqual(response.json, dict(description="Service broker requires version 2.13+."))

    def test_returns_400_if_request_not_contains_version_header(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)

    def test_returns_500_with_json_body_if_exception_was_raised(self):
        self.broker.deprovision.side_effect = Exception("Boooom!")

        response = self.client.delete(
            "/v2/service_instances/abc?plan_id=a&service_id=service-guid-here",
            headers={
                'Authorization': self.auth_header,
                'X-Broker-Api-Version': '2.13',
            })

        self.assertEqual(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json["description"], "Boooom!")

    def test_returns_500_with_json_body_if_service_exception_was_raised(self):
        self.broker.deprovision.side_effect = errors.ServiceExeption("Boooom!")

        response = self.client.delete(
            "/v2/service_instances/abc?plan_id=a&service_id=service-guid-here",
            headers={
                'Authorization': self.auth_header,
                'X-Broker-Api-Version': '2.13',
            })

        self.assertEqual(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json["description"], "Boooom!")
