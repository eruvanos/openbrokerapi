import http

from openbrokerapi.catalog import ServicePlan
from tests import BrokerTestCase
from openbrokerapi import errors
from openbrokerapi.service_broker import (
    DeprovisionServiceSpec,
    DeprovisionDetails,
    Service,
)


class DeprovisioningTest(BrokerTestCase):
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

    def test_deprovisioning_is_called_with_the_right_values(self):
        self.broker.deprovision.return_value = DeprovisionServiceSpec(
            False, "operation_str"
        )

        self.client.delete(
            "/v2/service_instances/here_instance_id?service_id=service-guid-here&plan_id=plan-guid-here&accepts_incomplete=true",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        (
            actual_instance_id,
            actual_details,
            actual_async_allowed,
        ) = self.broker.deprovision.call_args[1].values()
        self.assertEqual(actual_instance_id, "here_instance_id")

        self.assertIsInstance(actual_details, DeprovisionDetails)
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_async_allowed, True)

    def test_deprovisioning_called_just_with_required_fields(self):
        self.broker.deprovision.return_value = DeprovisionServiceSpec(
            False, "operation_str"
        )

        self.client.delete(
            "/v2/service_instances/here_instance_id?service_id=service-guid-here&plan_id=plan-guid-here",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        (
            actual_instance_id,
            actual_details,
            actual_async_allowed,
        ) = self.broker.deprovision.call_args[1].values()
        self.assertEqual(actual_instance_id, "here_instance_id")

        self.assertIsInstance(actual_details, DeprovisionDetails)
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_async_allowed, False)

    def test_returns_200_if_deleted(self):
        self.broker.deprovision.return_value = DeprovisionServiceSpec(
            False, "operation_str"
        )

        response = self.client.delete(
            "/v2/service_instances/abc?service_id=service-guid-here&plan_id=plan-guid-here",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json, dict())

    def test_returns_202_if_deletion_is_in_progress(self):
        self.broker.deprovision.return_value = DeprovisionServiceSpec(
            True, "operation_str"
        )

        response = self.client.delete(
            "/v2/service_instances/abc?service_id=service-guid-here&plan_id=plan-guid-here",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(http.HTTPStatus.ACCEPTED, response.status_code)
        self.assertEqual(response.json, dict(operation="operation_str"))

    def test_returns_410_if_service_instance_already_gone(self):
        self.broker.deprovision.side_effect = errors.ErrInstanceDoesNotExist()

        response = self.client.delete(
            "/v2/service_instances/abc?service_id=service-guid-here&plan_id=plan-guid-here",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(response.status_code, http.HTTPStatus.GONE)
        self.assertEqual(response.json, dict())

    def test_returns_422_if_async_not_supported_but_required(self):
        self.broker.deprovision.side_effect = errors.ErrAsyncRequired()

        response = self.client.delete(
            "/v2/service_instances/abc?service_id=service-guid-here&plan_id=plan-guid-here",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.json,
            dict(
                error="AsyncRequired",
                description="This service plan requires client support for asynchronous service operations.",
            ),
        )

    def test_returns_422_if_instance_is_in_use(self):
        self.broker.deprovision.side_effect = errors.ErrConcurrentInstanceAccess()

        response = self.client.delete(
            "/v2/service_instances/abc?service_id=service-guid-here&plan_id=plan-guid-here",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.json,
            dict(
                description="The Service Broker does not support concurrent requests that mutate the same resource.",
                error="ConcurrencyError",
            ),
        )

    def test_returns_401_if_request_not_contain_auth_header(self):
        response = self.client.delete(
            "/v2/service_instances/abc", headers={"X-Broker-Api-Version": "2.13"}
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)
