import http
import json

import openbrokerapi
from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan, Schemas
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
                    ServicePlan('plan-guid-here', name='', description='',
                                schemas=Schemas(service_instance=
                                               {"create": {
                                                   "parameters": {
                                                       "$schema": "http://json-schema.org/draft-04/schema#",
                                                       "type": "object",
                                                       "properties": {
                                                           "parameter1": {"type": "integer"}
                                                       },
                                                       "required": ["parameter1"]
                                                   }
                                               }}))
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

    def test_provisioning_called_with_the_wrong_values(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(dashboard_url="dash_url", operation="operation_str")

        response = self.client.put(
            "/v2/service_instances/here-instance-id?accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
                "parameters": {
                    "parameter1": "badtype"
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

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json["error"], "InvalidParameters")

    def test_provisining_called_without_parameters(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(dashboard_url="dash_url", operation="operation_str")

        response = self.client.put(
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

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json["error"], "InvalidParameters")
