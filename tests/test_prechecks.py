import http
import base64

from openbrokerapi import errors, constants
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import Service
from tests import BrokerTestCase


class PrecheckTest(BrokerTestCase):
    def setUp(self):
        self.broker.catalog.return_value = [
            Service(
                id="service-guid-here",
                name="",
                description="",
                bindable=True,
                plans=[ServicePlan("plan-guid-here", name="", description="")],
            )
        ]

    def test_returns_401_if_request_not_contain_auth_header(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                "X-Broker-Api-Version": "2.13",
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_returns_412_if_version_is_not_supported(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                "X-Broker-Api-Version": "2.9",
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.PRECONDITION_FAILED)

    def test_returns_412_with_message_if_version_is_not_supported(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                "X-Broker-Api-Version": "2.9",
            },
        )

        self.assertNotEqual(response.data, b"")
        self.assertEqual(response.json, {"description": "Service broker requires version 2.13+."})

    def test_returns_400_if_request_not_contains_version_header(self):
        response = self.client.put("/v2/service_instances/abc", headers={"Authorization": self.auth_header})

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)

    def test_returns_400_if_request_contains_originating_identity_header_with_missing_value(
        self,
    ):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                "Authorization": self.auth_header,
                "X-Broker-Api-Version": "2.13",
                "X-Broker-Api-Originating-Identity": "   test   ",  # missing value
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json,
            {
                "description": 'Improper "X-Broker-API-Originating-Identity" header. not enough values to unpack (expected 2, got 1)'
            },
        )

    def test_returns_400_if_request_contains_originating_identity_header_with_improper_base64_value(
        self,
    ):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                "Authorization": self.auth_header,
                "X-Broker-Api-Version": "2.13",
                "X-Broker-Api-Originating-Identity": "test bad64encoding",  # bad base64
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertIn(
            'Improper "X-Broker-API-Originating-Identity" header.',
            response.json["description"],
        )

    def test_returns_400_if_request_contains_originating_identity_header_with_improper_json_value(
        self,
    ):
        response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                "Authorization": self.auth_header,
                "X-Broker-Api-Version": "2.13",
                "X-Broker-Api-Originating-Identity": "test "
                + base64.standard_b64encode(b'{"test:123}').decode("ascii"),  # bad json
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json,
            {
                "description": 'Improper "X-Broker-API-Originating-Identity" header. Unterminated string starting at: line 1 column 2 (char 1)'
            },
        )

    def test_returns_500_with_json_body_if_exception_was_raised(self):
        self.broker.deprovision.side_effect = Exception("Boooom!")

        response = self.client.delete(
            "/v2/service_instances/abc?plan_id=plan-guid-here&service_id=service-guid-here",
            headers={
                "Authorization": self.auth_header,
                "X-Broker-Api-Version": "2.13",
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json["description"], constants.DEFAULT_EXCEPTION_ERROR_MESSAGE)

    def test_returns_500_with_json_body_if_service_exception_was_raised(self):
        self.broker.deprovision.side_effect = errors.ServiceException("Boooom!")

        response = self.client.delete(
            "/v2/service_instances/abc?plan_id=plan-guid-here&service_id=service-guid-here",
            headers={
                "Authorization": self.auth_header,
                "X-Broker-Api-Version": "2.13",
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json["description"], constants.DEFAULT_EXCEPTION_ERROR_MESSAGE)

    def test_returns_400_if_request_did_not_include_data(self):
        response = self.client.put(
            "/v2/service_instances/here-instance-id?accepts_incomplete=true",
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
