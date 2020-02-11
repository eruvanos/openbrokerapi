import json

from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import Service
from tests import BrokerTestCase


class BadRequest(BrokerTestCase):
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

    def test_provisioning_wrapps_bad_request(self):
        self.broker.provision.side_effect = errors.ErrBadRequest('BadRequest')

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
        self.assert400(response)

    def test_bind_called_with_the_right_values(self):
        self.broker.bind.side_effect = errors.ErrBadRequest('BadRequest')

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {
                    "app_guid": "app-guid-here",
                    "route": "route-here"
                },
                "parameters": {
                    "parameter1": 1
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assert400(response)

    def test_update_wraps_bad_request(self):
        self.broker.update.side_effect = errors.ErrBadRequest('BadRequest')

        response = self.client.patch(
            "/v2/service_instances/here-service-instance-id?accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "parameters": {
                    "parameter1": 1
                },
                "previous_values": {
                    "plan_id": "old-plan-guid-here",
                    "service_id": "service-guid-here",
                    "organization_id": "org-guid-here",
                    "space_id": "space-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assert400(response)

    def test_unbind_is_called_with_the_right_values(self):
        self.broker.unbind.side_effect = errors.ErrBadRequest('BadRequest')

        query = "service_id=service-guid-here&plan_id=plan-guid-here"
        response = self.client.delete(
            "/v2/service_instances/here_instance_id/service_bindings/here_binding_id?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assert400(response)

    def test_deprovisioning_is_called_with_the_right_values(self):
        self.broker.deprovision.side_effect = errors.ErrBadRequest('BadRequest')

        response = self.client.delete(
            "/v2/service_instances/here_instance_id?service_id=service-guid-here&plan_id=plan-guid-here&accepts_incomplete=true",
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assert400(response)