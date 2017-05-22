import http
import json

from werkzeug.wrappers import Response

from test import BrokerTestCase
from openbrokerapi import errors
from openbrokerapi.service_broker import UpdateServiceSpec


class ProvisioningTest(BrokerTestCase):
    def test_returns_200_if_updated(self):
        self.broker.update.return_value = UpdateServiceSpec(False, "operation")

        response: Response = self.client.patch(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "parameters": {
                    "parameter1": 1,
                    "parameter2": "foo"
                },
                "previous_values": {
                    "plan_id": "old-plan-guid-here",
                    "service_id": "service-guid-here",
                    "organization_id": "org-guid-here",
                    "space_id": "space-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.OK)
        self.assertEquals(response.json, dict())

    def test_returns_202_if_update_is_in_progress(self):
        self.broker.update.return_value = UpdateServiceSpec(True, "operation")

        response: Response = self.client.patch(
            "/v2/service_instances/abc?accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "parameters": {
                    "parameter1": 1,
                    "parameter2": "foo"
                },
                "previous_values": {
                    "plan_id": "old-plan-guid-here",
                    "service_id": "service-guid-here",
                    "organization_id": "org-guid-here",
                    "space_id": "space-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.ACCEPTED)
        self.assertEquals(response.json, dict(
            operation="operation"
        ))

    def test_returns_422_if_async_required_but_not_supported(self):
        self.broker.update.side_effect = errors.ErrAsyncRequired()

        response: Response = self.client.patch(
            "/v2/service_instances/abc?accepts_incomplete=false",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "parameters": {
                    "parameter1": 1,
                    "parameter2": "foo"
                },
                "previous_values": {
                    "plan_id": "old-plan-guid-here",
                    "service_id": "service-guid-here",
                    "organization_id": "org-guid-here",
                    "space_id": "space-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEquals(response.json, dict(
            error="AsyncRequired",
            description="This service plan requires client support for asynchronous service operations."
        ))

    def test_returns_401_if_request_not_contain_auth_header(self):
        response: Response = self.client.patch(
            "/v2/service_instances/abc",
            headers={
                'X-Broker-Api-Version': '2.00'
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNAUTHORIZED)
