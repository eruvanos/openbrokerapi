import http
import json

from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import (
    UpdateServiceSpec,
    UpdateDetails,
    PreviousValues,
    Service,
)
from tests import BrokerTestCase


class UpdateTest(BrokerTestCase):
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

    def test_update_called_with_the_right_values(self):
        self.broker.update.return_value = UpdateServiceSpec(False, "operation")

        self.client.patch(
            "/v2/service_instances/here-service-instance-id?accepts_incomplete=true",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "parameters": {"parameter1": 1},
                    "previous_values": {
                        "plan_id": "old-plan-guid-here",
                        "service_id": "service-guid-here",
                        "organization_id": "org-guid-here",
                        "space_id": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        actual_service_id, actual_details, actual_async = self.broker.update.call_args[1].values()
        self.assertEqual(actual_service_id, "here-service-instance-id")
        self.assertEqual(actual_async, True)

        self.assertIsInstance(actual_details, UpdateDetails)
        self.assertIsInstance(actual_details.previous_values, PreviousValues)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.parameters, {"parameter1": 1})
        self.assertEqual(actual_details.previous_values.plan_id, "old-plan-guid-here")
        self.assertEqual(actual_details.previous_values.service_id, "service-guid-here")
        self.assertEqual(actual_details.previous_values.organization_id, "org-guid-here")
        self.assertEqual(actual_details.previous_values.space_id, "space-guid-here")

    def test_update_callable_including_only_required_fields(self):
        self.broker.update.return_value = UpdateServiceSpec(False, "operation")

        self.client.patch(
            "/v2/service_instances/here-service-instance-id",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        actual_instance_id, actual_details, actual_async = self.broker.update.call_args[1].values()
        self.assertEqual(actual_instance_id, "here-service-instance-id")
        self.assertEqual(actual_async, False)

        self.assertIsInstance(actual_details, UpdateDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")

        self.assertIsNone(actual_details.plan_id)
        self.assertIsNone(actual_details.parameters)
        self.assertIsNone(actual_details.previous_values)

    def test_update_can_change_dashboard_url(self):
        new_dashboard_url = "https://new.dashboard/"
        self.broker.update.return_value = UpdateServiceSpec(
            is_async=False, operation=None, dashboard_url=new_dashboard_url
        )

        response = self.client.patch(
            "/v2/service_instances/here-service-instance-id",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual({"dashboard_url": new_dashboard_url}, response.json)

    def test_update_ignores_unknown_parameters(self):
        self.broker.update.return_value = UpdateServiceSpec(False, "operation")

        self.client.patch(
            "/v2/service_instances/here-service-instance-id?accepts_incomplete=true",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "unknown": "unknown",
                    "parameters": {"parameter1": 1},
                    "previous_values": {
                        "unknown": "unknown",
                        "plan_id": "old-plan-guid-here",
                        "service_id": "service-guid-here",
                        "organization_id": "org-guid-here",
                        "space_id": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        actual_service_id, actual_details, actual_async = self.broker.update.call_args[1].values()
        self.assertEqual(actual_service_id, "here-service-instance-id")
        self.assertEqual(actual_async, True)

        self.assertIsInstance(actual_details, UpdateDetails)
        self.assertIsInstance(actual_details.previous_values, PreviousValues)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.parameters, {"parameter1": 1})
        self.assertEqual(actual_details.previous_values.plan_id, "old-plan-guid-here")
        self.assertEqual(actual_details.previous_values.service_id, "service-guid-here")
        self.assertEqual(actual_details.previous_values.organization_id, "org-guid-here")
        self.assertEqual(actual_details.previous_values.space_id, "space-guid-here")

    def test_returns_200_if_updated(self):
        self.broker.update.return_value = UpdateServiceSpec(False, "operation")

        response = self.client.patch(
            "/v2/service_instances/abc",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "previous_values": {
                        "plan_id": "old-plan-guid-here",
                        "service_id": "service-guid-here",
                        "organization_id": "org-guid-here",
                        "space_id": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json, {})

    def test_returns_202_if_update_is_in_progress(self):
        self.broker.update.return_value = UpdateServiceSpec(True, "operation")

        response = self.client.patch(
            "/v2/service_instances/abc?accepts_incomplete=true",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "previous_values": {
                        "plan_id": "old-plan-guid-here",
                        "service_id": "service-guid-here",
                        "organization_id": "org-guid-here",
                        "space_id": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.ACCEPTED)
        self.assertEqual(response.json, {"operation": "operation"})

    def test_returns_422_if_async_required_but_not_supported(self):
        self.broker.update.side_effect = errors.ErrAsyncRequired()

        response = self.client.patch(
            "/v2/service_instances/abc?accepts_incomplete=false",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "previous_values": {
                        "plan_id": "old-plan-guid-here",
                        "service_id": "service-guid-here",
                        "organization_id": "org-guid-here",
                        "space_id": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.json,
            {
                "error": "AsyncRequired",
                "description": "This service plan requires client support for asynchronous service operations.",
            },
        )

    def test_returns_400_if_missing_mandatory_data(self):
        self.broker.update.side_effect = errors.ErrInvalidParameters("Required parameters not provided.")

        response = self.client.patch(
            "/v2/service_instances/abc?accepts_incomplete=false",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "previous_values": {
                        "plan_id": "old-plan-guid-here",
                        "service_id": "service-guid-here",
                        "organization_id": "org-guid-here",
                        "space_id": "space-guid-here",
                    },
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json,
            {
                "error": "InvalidParameters",
                "description": "Required parameters not provided.",
            },
        )

    def test_returns_401_if_request_does_not_contain_auth_header(self):
        response = self.client.patch(
            "/v2/service_instances/abc",
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_returns_400_if_request_does_not_contain_content_type_header(self):
        response = self.client.patch(
            "/v2/service_instances/abc",
            headers={"X-Broker-Api-Version": "2.13", "Authorization": self.auth_header},
        )

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json,
            {"description": 'Improper Content-Type header. Expecting "application/json"'},
        )

    def test_returns_400_if_request_does_not_contain_valid_json_body(self):
        response = self.client.patch(
            "/v2/service_instances/abc",
            data="I am not a json object",
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json,
            {"description": 'Improper Content-Type header. Expecting "application/json"'},
        )

    def test_returns_422_if_instance_is_in_use(self):
        self.broker.update.side_effect = errors.ErrConcurrentInstanceAccess()

        response = self.client.patch(
            "/v2/service_instances/abc",
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                }
            ),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header,
            },
        )

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.json,
            {
                "description": "The Service Broker does not support concurrent requests that mutate the same resource.",
                "error": "ConcurrencyError",
            },
        )
