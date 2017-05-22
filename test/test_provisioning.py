import http
import json

from werkzeug.wrappers import Response

from test import BrokerTestCase
from openbrokerapi import errors
from openbrokerapi.service_broker import ProvisionedServiceSpec


class ProvisioningTest(BrokerTestCase):
    def test_returns_201_if_created(self):
        self.broker.provision.return_value = ProvisionedServiceSpec("dash_url", "operation_str")

        response: Response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.CREATED)
        self.assertEquals(response.json, dict(
            dashboard_url="dash_url",
            operation="operation_str"
        ))

    def test_returns_409_if_already_exists_but_is_not_equal(self):
        self.broker.provision.side_effect = errors.ErrInstanceAlreadyExists()

        response: Response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.CONFLICT)
        self.assertEquals(response.json, {})

    def test_returns_422_if_async_required_but_not_supported(self):
        self.broker.provision.side_effect = errors.ErrAsyncRequired()

        response: Response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
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
        response: Response = self.client.put(
            "/v2/service_instances/abc",
            headers={
                'X-Broker-Api-Version': '2.00',
            })

        self.assertEquals(response.status_code, http.HTTPStatus.UNAUTHORIZED)
