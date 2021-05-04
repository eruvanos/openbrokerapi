import http
import json

from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import Binding, BindDetails, BindResource, VolumeMount, SharedDevice, BindState, \
    Service
from tests import BrokerTestCase

expected_credentials = {"uri": "mysql://mysqluser:pass@mysqlhost:3306/dbname",
                        "username": "mysqluser",
                        "password": "pass",
                        "host": "mysqlhost",
                        "port": 3306,
                        "database": "dbname"}


class BindTest(BrokerTestCase):
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

    def test_bind_called_with_the_right_values(self):
        self.broker.bind.return_value = Binding(
            credentials=expected_credentials
        )

        self.client.put(
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

        actual_instance_id, actual_binding_id, actual_details, async_allowed = self.broker.bind.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance_id")
        self.assertEqual(actual_binding_id, "here-binding_id")

        self.assertIsInstance(actual_details, BindDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")
        self.assertEqual(actual_details.parameters, dict(parameter1=1))

        self.assertIsInstance(actual_details.bind_resource, BindResource)
        self.assertEqual(actual_details.bind_resource.app_guid, "app-guid-here")
        self.assertEqual(actual_details.bind_resource.route, "route-here")

        self.assertFalse(async_allowed)

    def test_bind_called_just_with_required_fields(self):
        self.broker.bind.return_value = Binding(
            credentials=expected_credentials
        )

        self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here"
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_binding_id, actual_details, async_allowed = self.broker.bind.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance_id")
        self.assertEqual(actual_binding_id, "here-binding_id")

        self.assertIsInstance(actual_details, BindDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")

        self.assertIsNone(actual_details.app_guid)
        self.assertIsNone(actual_details.parameters)
        self.assertIsNone(actual_details.bind_resource)

        self.assertFalse(async_allowed)

    def test_bind_ignores_unknown_parameters(self):
        self.broker.bind.return_value = Binding(
            credentials=expected_credentials
        )

        self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "unknown": "unknown",
                "bind_resource": {
                    "unknown": "unknown"
                },
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        actual_instance_id, actual_binding_id, actual_details, async_allowed = self.broker.bind.call_args[0]
        self.assertEqual(actual_instance_id, "here-instance_id")
        self.assertEqual(actual_binding_id, "here-binding_id")

        self.assertIsInstance(actual_details, BindDetails)
        self.assertEqual(actual_details.service_id, "service-guid-here")
        self.assertEqual(actual_details.plan_id, "plan-guid-here")

        self.assertIsNone(actual_details.app_guid)
        self.assertIsNone(actual_details.parameters)
        self.assertIsNotNone(actual_details.bind_resource)

        self.assertFalse(async_allowed)

    def test_returns_201_if_binding_has_been_created(self):
        self.broker.bind.return_value = Binding(
            credentials=expected_credentials
        )

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {
                    "app_guid": "app-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)
        self.assertEqual(response.json, dict(
            credentials=expected_credentials
        ))

    def test_returns_202_for_async_binding(self):
        self.broker.bind.return_value = Binding(
            state=BindState.IS_ASYNC,
            operation='bind'
        )

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id&accepts_incomplete=true",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {
                    "app_guid": "app-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(http.HTTPStatus.ACCEPTED, response.status_code)
        self.assertEqual(response.json, {'operation': 'bind'})

    def test_supports_volume_mounts(self):
        self.broker.bind.return_value = Binding(
            volume_mounts=[
                VolumeMount(
                    driver="",
                    container_dir="",
                    mode="",
                    device_type="",
                    device=SharedDevice(
                        volume_id="",
                        mount_config=dict(config1="1")
                    )
                )
            ]
        )

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {
                    "app_guid": "app-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)
        self.assertEqual(response.json, dict(
            volume_mounts=[
                dict(
                    driver="",
                    container_dir="",
                    mode="",
                    device_type="",
                    device=dict(
                        volume_id="",
                        mount_config=dict(config1="1")
                    )
                )
            ]
        ))

    def test_returns_409_if_binding_already_exists(self):
        self.broker.bind.side_effect = errors.ErrBindingAlreadyExists()

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {
                    "app_guid": "app-guid-here"
                }
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.CONFLICT)
        self.assertEqual(response.json, dict())

    def test_returns_422_if_app_guid_is_required_but_not_given(self):
        self.broker.bind.side_effect = errors.ErrAppGuidNotProvided()

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {}
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json, dict(
            error="RequiresApp",
            description="This service supports generation of credentials through binding an application only."
        ))

    def test_returns_401_if_request_does_not_contain_auth_header(self):
        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({}),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json'
            })

        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_returns_400_if_request_does_not_contain_content_type_header(self):
        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({}),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json, dict(description='Improper Content-Type header. Expecting "application/json"'))

    def test_returns_400_if_request_does_not_contain_valid_json_body(self):
        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data='I am not a json object',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json, dict(description='Improper Content-Type header. Expecting "application/json"'))

    def test_returns_200_if_identical_binding_already_exists(self):
        self.broker.bind.return_value = Binding(state=BindState.IDENTICAL_ALREADY_EXISTS)

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {}
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json, dict())

    def test_returns_422_if_instance_is_in_use(self):
        self.broker.bind.side_effect = errors.ErrConcurrentInstanceAccess()

        response = self.client.put(
            "/v2/service_instances/here-instance_id/service_bindings/here-binding_id",
            data=json.dumps({
                "service_id": "service-guid-here",
                "plan_id": "plan-guid-here",
                "bind_resource": {}
            }),
            headers={
                'X-Broker-Api-Version': '2.13',
                'Content-Type': 'application/json',
                'Authorization': self.auth_header
            })

        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json, dict(
            description='The Service Broker does not support concurrent requests that mutate the same resource.',
            error='ConcurrencyError'
        ))
