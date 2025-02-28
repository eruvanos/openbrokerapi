import http

from openbrokerapi.catalog import ServicePlan
from tests import BrokerTestCase
from openbrokerapi import errors
from openbrokerapi.service_broker import UnbindDetails, Service, UnbindSpec


class UnbindTest(BrokerTestCase):
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

    def test_unbind_is_called_with_the_right_values(self):
        self.broker.unbind.return_value = UnbindSpec(False)

        query = "service_id=service-guid-here&plan_id=plan-guid-here"
        self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        (
            actual_instance_id,
            actual_binding_id,
            actual_details,
            async_allowed,
        ) = self.broker.unbind.call_args[1].values()
        self.assertEqual(actual_instance_id, "here_instance_id")
        self.assertEqual(actual_binding_id, "here_binding_id")

        self.assertIsInstance(actual_details, UnbindDetails)
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertFalse(async_allowed)

    def test_returns_200_if_binding_has_been_deleted(self):
        self.broker.unbind.return_value = UnbindSpec(False)

        query = "service_id=service-guid-here&plan_id=plan-guid-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(http.HTTPStatus.OK, response.status_code)
        self.assertEqual(response.json, {})

    def test_returns_202_for_async(self):
        self.broker.unbind.return_value = UnbindSpec(True, operation="unbind")

        query = "service_id=service-guid-here&plan_id=plan-guid-here&accepts_incomplete=true"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(http.HTTPStatus.ACCEPTED, response.status_code)
        self.assertEqual(response.json, {"operation": "unbind"})

    def test_returns_410_if_binding_does_not_exists(self):
        self.broker.unbind.side_effect = errors.ErrBindingDoesNotExist()

        query = "service_id=service-guid-here&plan_id=plan-guid-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(response.status_code, http.HTTPStatus.GONE)
        self.assertEqual(response.json, {})

    def test_returns_400_if_request_not_contain_auth_header(self):
        query = "service_id=service-guid-here&plan_id=plan-guid-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                "X-Broker-Api-Version": "2.13",
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_returns_422_if_instance_is_in_use(self):
        self.broker.unbind.side_effect = errors.ErrConcurrentInstanceAccess()

        query = "service_id=service-guid-here&plan_id=plan-guid-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.json,
            {
                "description": "The Service Broker does not support concurrent requests that mutate the same resource.",
                "error": "ConcurrencyError",
            },
        )

    def test_returns_422_if_async_required_but_not_supported(self):
        self.broker.unbind.side_effect = errors.ErrAsyncRequired()

        query = "service_id=service-guid-here&plan_id=plan-guid-here&accepts_incomplete=true"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )
        self.broker.bind.side_effect = errors.ErrAsyncRequired()

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.json,
            {
                "description": "This service plan requires client support for asynchronous service operations.",
                "error": "AsyncRequired",
            },
        )
