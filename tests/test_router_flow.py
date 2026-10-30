import base64
import json
import logging
from http import HTTPStatus
from typing import ClassVar, Optional

from flask import Flask
from flask_testing import TestCase

from openbrokerapi import errors
from openbrokerapi.api import get_blueprint
from openbrokerapi.auth import BrokerCredentials
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.log_util import basic_config
from openbrokerapi.router import Router
from openbrokerapi.service_broker import (
    ServiceBroker,
    Service,
    ProvisionDetails,
    ProvisionedServiceSpec,
    ProvisionState,
    BindDetails,
    Binding,
    BindState,
    GetInstanceDetailsSpec,
    GetBindingSpec,
    LastOperation,
    OperationState,
)


class AsyncInMemoryBroker(ServiceBroker):
    """
    Provisions and binds asynchronously. Operations complete on the first poll.
    """

    def __init__(self, service_id: str, plan_id: str):
        self.service_id = service_id
        self.plan_id = plan_id
        self.instances = {}
        self.bindings = {}
        self.async_allowed_calls = []

    def catalog(self) -> Service:
        return Service(
            id=self.service_id,
            name=self.service_id,
            description=self.service_id,
            bindable=True,
            plans=[ServicePlan(id=self.plan_id, name="standard", description="standard")],
            instances_retrievable=True,
            bindings_retrievable=True,
        )

    def provision(
        self, instance_id: str, details: ProvisionDetails, async_allowed: bool, **kwargs
    ) -> ProvisionedServiceSpec:
        self.async_allowed_calls.append(("provision", async_allowed))
        if not async_allowed:
            raise errors.ErrAsyncRequired()
        self.instances[instance_id] = details
        return ProvisionedServiceSpec(state=ProvisionState.IS_ASYNC, operation="provision-" + instance_id)

    def bind(self, instance_id: str, binding_id: str, details: BindDetails, async_allowed: bool, **kwargs) -> Binding:
        self.async_allowed_calls.append(("bind", async_allowed))
        if not async_allowed:
            raise errors.ErrAsyncRequired()
        self.bindings[(instance_id, binding_id)] = {"user": self.service_id}
        return Binding(state=BindState.IS_ASYNC, operation="bind-" + binding_id)

    def last_operation(
        self,
        instance_id: str,
        operation_data: Optional[str],
        service_id: Optional[str],
        plan_id: Optional[str],
        **kwargs,
    ) -> LastOperation:
        if operation_data != "provision-" + instance_id:
            raise errors.ErrInvalidParameters("unexpected operation " + str(operation_data))
        return LastOperation(OperationState.SUCCEEDED, self.service_id)

    def last_binding_operation(
        self,
        instance_id: str,
        binding_id: str,
        operation_data: Optional[str],
        service_id: Optional[str],
        plan_id: Optional[str],
        **kwargs,
    ) -> LastOperation:
        if operation_data != "bind-" + binding_id:
            raise errors.ErrInvalidParameters("unexpected operation " + str(operation_data))
        return LastOperation(OperationState.SUCCEEDED, self.service_id)

    def get_instance(self, instance_id: str, **kwargs) -> GetInstanceDetailsSpec:
        if instance_id not in self.instances:
            raise errors.ErrInstanceDoesNotExist()
        details = self.instances[instance_id]
        return GetInstanceDetailsSpec(service_id=details.service_id, plan_id=details.plan_id)

    def get_binding(self, instance_id: str, binding_id: str, **kwargs) -> GetBindingSpec:
        if (instance_id, binding_id) not in self.bindings:
            raise errors.ErrBindingDoesNotExist()
        return GetBindingSpec(credentials=self.bindings[(instance_id, binding_id)])


class RouterFlowTest(TestCase):
    headers: ClassVar[dict] = {
        "X-Broker-API-Version": "2.17",
        "Authorization": "Basic " + base64.b64encode(b":").decode("ascii"),
    }

    def create_app(self):
        self.broker_a = AsyncInMemoryBroker("service-a", "plan-a")
        self.broker_b = AsyncInMemoryBroker("service-b", "plan-b")
        router = Router(self.broker_a, self.broker_b)

        app = Flask(__name__)
        app.register_blueprint(get_blueprint(router, BrokerCredentials("", ""), basic_config(level=logging.CRITICAL)))
        return app

    def test_async_flows_for_both_brokers(self):
        for broker in (self.broker_a, self.broker_b):
            with self.subTest(service_id=broker.service_id):
                self.check_async_flow(broker)

    def check_async_flow(self, broker: AsyncInMemoryBroker):
        instance_id = "instance-" + broker.service_id
        binding_id = "binding-" + broker.service_id
        other = self.broker_b if broker is self.broker_a else self.broker_a

        # PROVISION (async)
        response = self.client.put(
            f"/v2/service_instances/{instance_id}?accepts_incomplete=true",
            data=json.dumps(
                {
                    "service_id": broker.service_id,
                    "plan_id": broker.plan_id,
                    "organization_guid": "org",
                    "space_guid": "space",
                }
            ),
            content_type="application/json",
            headers=self.headers,
        )
        self.assertEqual(HTTPStatus.ACCEPTED, response.status_code)
        operation = response.json["operation"]
        self.assertEqual(f"{broker.service_id} provision-{instance_id}", operation)

        # POLL provision
        response = self.client.get(
            f"/v2/service_instances/{instance_id}/last_operation",
            query_string={"operation": operation, "service_id": broker.service_id, "plan_id": broker.plan_id},
            headers=self.headers,
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"state": "succeeded", "description": broker.service_id}, response.json)

        # BIND (async)
        response = self.client.put(
            f"/v2/service_instances/{instance_id}/service_bindings/{binding_id}?accepts_incomplete=true",
            data=json.dumps({"service_id": broker.service_id, "plan_id": broker.plan_id}),
            content_type="application/json",
            headers=self.headers,
        )
        self.assertEqual(HTTPStatus.ACCEPTED, response.status_code)
        operation = response.json["operation"]
        self.assertEqual(f"{broker.service_id} bind-{binding_id}", operation)

        # POLL bind
        response = self.client.get(
            f"/v2/service_instances/{instance_id}/service_bindings/{binding_id}/last_operation",
            query_string={"operation": operation, "service_id": broker.service_id, "plan_id": broker.plan_id},
            headers=self.headers,
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"state": "succeeded", "description": broker.service_id}, response.json)

        # GET instance
        response = self.client.get(f"/v2/service_instances/{instance_id}", headers=self.headers)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"service_id": broker.service_id, "plan_id": broker.plan_id}, response.json)

        # GET binding
        response = self.client.get(
            f"/v2/service_instances/{instance_id}/service_bindings/{binding_id}", headers=self.headers
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"credentials": {"user": broker.service_id}}, response.json)

        # async_allowed passed through unchanged, and only to the owning broker
        self.assertEqual([("provision", True), ("bind", True)], broker.async_allowed_calls)
        self.assertNotIn(instance_id, other.instances)

    def test_async_allowed_false_is_passed_through(self):
        response = self.client.put(
            "/v2/service_instances/i1/service_bindings/b1?accepts_incomplete=false",
            data=json.dumps({"service_id": "service-b", "plan_id": "plan-b"}),
            content_type="application/json",
            headers=self.headers,
        )

        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)
        self.assertEqual([("bind", False)], self.broker_b.async_allowed_calls)
        self.assertEqual([], self.broker_a.async_allowed_calls)

    def test_get_unknown_instance_and_binding_return_404(self):
        response = self.client.get("/v2/service_instances/unknown", headers=self.headers)
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

        response = self.client.get("/v2/service_instances/unknown/service_bindings/unknown", headers=self.headers)
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
