import http

from flask.wrappers import Response

from test import BrokerTestCase


class PrecheckTest(BrokerTestCase):
    def test_returns_401_if_request_not_contain_auth_header(self):
        response: Response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                'X-Broker-Api-Version': '2.00',
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_returns_412_if_version_is_not_supported(self):
        response: Response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                'X-Broker-Api-Version': '1.00',
            })

        self.assertEquals(response.status_code, http.HTTPStatus.PRECONDITION_FAILED)
        self.assertEquals(response.json, dict(description="Service broker requires version 2.0+."))

    def test_returns_400_if_request_not_contains_version_header(self):
        response: Response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.BAD_REQUEST)

    def test_returns_500_with_json_body_if_exception_was_raised(self):
        self.broker.deprovision.side_effect=Exception("Boooom!")

        response: Response = self.client.delete(
            "/v2/service_instances/abc?plan_id=a&service_id=b",
            headers={
                'Authorization': self.auth_header,
                'X-Broker-Api-Version': '2.00',
            })

        self.assertEquals(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIsNotNone(response.json["description"])
