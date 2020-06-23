import http
import json

from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import ProvisionedServiceSpec, ProvisionDetails, ProvisionState, Service
from tests import BrokerTestCase


class ProvisioningTest(BrokerTestCase):
    def setUp(self):
        self.broker.catalog.return_value = [
            Service(
                id='service-guid-here',
                name='',
                description='',
                bindable=True,
                plans=[
                    ServicePlan('plan-guid-here', name='', description='')
                ])
        ]

    def test_provisioning_called_with_the_right_values(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(dashboard_url="dash_url", operation="operation_str")

        self.client.put(
            "/v2/service_instances/here-instance-id?accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
                "parameters": {
                    "parameter1": 1
                },
                "context": {
                    "organization_guid": "org-guid-here",
                    "space_guid": "space-guid-here",
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_details, actual_async_allowed = self.broker.provision.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance-id")
        self.assertEqual(actual_async_allowed, True)

        self.assertIsInstance(actual_details, ProvisionDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.parameters, dict(parameter1=1))
        self.assertEqual(actual_details.organization_guid, "org-guid-here")
        self.assertEqual(actual_details.space_guid, "space-guid-here")
        self.assertEqual(actual_details.context["organization_guid"], "org-guid-here")
        self.assertEqual(actual_details.context["space_guid"], "space-guid-here")

    def test_provisining_called_just_with_required_fields(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(dashboard_url="dash_url", operation="operation_str")

        self.client.put(
            "/v2/service_instances/here-instance-id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "context": {
                    "organization_guid": "org-guid-here",
                    "space_guid": "space-guid-here",
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_details, actual_async_allowed = self.broker.provision.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance-id")
        self.assertEqual(actual_async_allowed, False)

        self.assertIsInstance(actual_details, ProvisionDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.organization_guid, "org-guid-here")
        self.assertEqual(actual_details.space_guid, "space-guid-here")

        self.assertIsNone(actual_details.parameters)

    def test_provisining_optional_org_and_space_if_available_in_context(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(dashboard_url="dash_url", operation="operation_str")

        self.client.put(
            "/v2/service_instances/here-instance-id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header
            })

        actual_instance_id, actual_details, actual_async_allowed = self.broker.provision.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance-id")
        self.assertEqual(actual_async_allowed, False)

        self.assertIsInstance(actual_details, ProvisionDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.organization_guid, "org-guid-here")
        self.assertEqual(actual_details.space_guid, "space-guid-here")

        self.assertIsNone(actual_details.parameters)

    def test_provisining_ignores_unknown_parameters(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(dashboard_url="dash_url", operation="operation_str")

        self.client.put(
            "/v2/service_instances/here-instance-id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
                "unknown": "unknown"
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_details, actual_async_allowed = self.broker.provision.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance-id")
        self.assertEqual(actual_async_allowed, False)

        self.assertIsInstance(actual_details, ProvisionDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.organization_guid, "org-guid-here")
        self.assertEqual(actual_details.space_guid, "space-guid-here")

        self.assertIsNone(actual_details.parameters)

    def test_returns_201_if_created(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(
            dashboard_url="dash_url",
            operation="operation_str"
        )

        response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)
        self.assertEqual(response.json, dict(
            dashboard_url="dash_url",
            operation="operation_str"
        ))

    def test_returns_202_if_provisioning_in_progress(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(
            ProvisionState.IS_ASYNC,
            "dash_url",
            "operation_str"
        )

        response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.ACCEPTED)
        self.assertEqual(response.json, dict(
            dashboard_url="dash_url",
            operation="operation_str"
        ))

    def test_returns_409_if_already_exists_but_is_not_equal(self):
        self.broker.provision.side_effect = errors.ErrInstanceAlreadyExists()

        response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.CONFLICT)
        self.assertEqual(response.json, {})

    def test_returns_422_if_async_required_but_not_supported(self):
        self.broker.provision.side_effect = errors.ErrAsyncRequired()

        response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json, dict(
            error="AsyncRequired",
            description="This service plan requires client support for asynchronous service operations."
        ))

    def test_returns_400_if_missing_mandatory_data(self):
        self.broker.provision.side_effect = errors.ErrInvalidParameters('Required parameters not provided.')

        response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                "X-Broker-Api-Version": "2.13",
                "Content-Type": "application/json",
                "Authorization": self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json, dict(
            error="InvalidParameters",
            description="Required parameters not provided."
        ))

    def test_returns_200_if_identical_service_exists(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(ProvisionState.IDENTICAL_ALREADY_EXISTS)

        response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json, dict())

    def test_returns_400_if_request_does_not_contain_content_type_header(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json,
                         dict(description='Improper Content-Type header. Expecting "application/json"'))

    def test_returns_400_if_request_does_not_contain_valid_json_body(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            data='I am not a json object',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json,
                         dict(description='Improper Content-Type header. Expecting "application/json"'))

    def test_returns_400_if_context_organization_guid_mismatch(self):
        response = self.client.put(
            "/v2/service_instances/here-instance-id?accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
                "parameters": {
                    "parameter1": 1
                },
                'context': {
                    "organization_guid": "a_mismatching_org",
                    "space_guid": "space-guid-here",
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json,
                         dict(description="organization_guid does not match with context.organization_guid"))

    def test_returns_400_if_context_space_guid_mismatch(self):
        response = self.client.put(
            "/v2/service_instances/here-instance-id?accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
                "parameters": {
                    "parameter1": 1
                },
                'context': {
                    "organization_guid": "org-guid-here",
                    "space_guid": "a_mismatching_space",
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json, dict(description="space_guid does not match with context.space_guid"))
