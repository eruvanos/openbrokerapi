import base64
import logging
from http import HTTPStatus
from typing import ClassVar

from flask import Flask
from flask_testing import TestCase

from openbrokerapi import errors
from openbrokerapi.api import get_blueprint
from openbrokerapi.auth import BrokerCredentials
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.log_util import basic_config
from openbrokerapi.router import Router
from openbrokerapi.service_broker import (
    GetBindingSpec,
    GetInstanceDetailsSpec,
    Service,
    ServiceBroker,
)
from tests import BrokerTestCase

AUTH_HEADER = "Basic " + base64.b64encode(b":").decode("ascii")
HEADERS = {"X-Broker-API-Version": "2.17", "Authorization": AUTH_HEADER}


class PlainBrokerFetchHintsTest(BrokerTestCase):
    """Hints are only used by the Router; plain brokers keep receiving the same arguments as before."""

    def test_instance_hints_are_not_passed_to_plain_broker(self):
        self.broker.get_instance.return_value = GetInstanceDetailsSpec("service-a", "plan-a")

        response = self.client.get(
            "/v2/service_instances/instance-1?service_id=service-a&plan_id=plan-a",
            headers=HEADERS,
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.broker.get_instance.assert_called_once_with(instance_id="instance-1")

    def test_binding_hints_are_not_passed_to_plain_broker(self):
        self.broker.get_binding.return_value = GetBindingSpec(credentials={"user": "u"})

        response = self.client.get(
            "/v2/service_instances/instance-1/service_bindings/binding-1?service_id=service-a&plan_id=plan-a",
            headers=HEADERS,
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.broker.get_binding.assert_called_once_with(instance_id="instance-1", binding_id="binding-1")


class RecordingBroker(ServiceBroker):
    """Owns exactly one instance and binding; records every fetch call it receives."""

    def __init__(self, service_id: str, plan_id: str):
        self.service_id = service_id
        self.plan_id = plan_id
        self.instances = set()
        self.bindings = set()
        self.calls = []

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

    def provision(self, instance_id, details, async_allowed, **kwargs):
        raise NotImplementedError()

    def bind(self, instance_id, binding_id, details, async_allowed, **kwargs):
        raise NotImplementedError()

    def get_instance(self, instance_id: str, **kwargs) -> GetInstanceDetailsSpec:
        self.calls.append(("get_instance", instance_id, kwargs))
        if instance_id not in self.instances:
            raise errors.ErrInstanceDoesNotExist()
        return GetInstanceDetailsSpec(service_id=self.service_id, plan_id=self.plan_id)

    def get_binding(self, instance_id: str, binding_id: str, **kwargs) -> GetBindingSpec:
        self.calls.append(("get_binding", (instance_id, binding_id), kwargs))
        if (instance_id, binding_id) not in self.bindings:
            raise errors.ErrBindingDoesNotExist()
        return GetBindingSpec(credentials={"user": self.service_id})


class RouterFetchHintsTest(TestCase):
    headers: ClassVar[dict] = HEADERS

    def create_app(self):
        self.broker_a = RecordingBroker("service-a", "plan-a")
        self.broker_b = RecordingBroker("service-b", "plan-b")
        self.broker_b.instances.add("instance-b")
        self.broker_b.bindings.add(("instance-b", "binding-b"))
        router = Router(self.broker_a, self.broker_b)

        app = Flask(__name__)
        app.register_blueprint(get_blueprint(router, BrokerCredentials("", ""), basic_config(level=logging.CRITICAL)))
        return app

    def test_instance_hint_routes_directly_to_named_broker(self):
        response = self.client.get(
            "/v2/service_instances/instance-b?service_id=service-b&plan_id=plan-b", headers=self.headers
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"service_id": "service-b", "plan_id": "plan-b"}, response.json)
        self.assertEqual([], self.broker_a.calls)
        self.assertEqual(
            [("get_instance", "instance-b", {})],
            self.broker_b.calls,
        )

    def test_binding_hint_routes_directly_to_named_broker(self):
        response = self.client.get(
            "/v2/service_instances/instance-b/service_bindings/binding-b?service_id=service-b",
            headers=self.headers,
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"credentials": {"user": "service-b"}}, response.json)
        self.assertEqual([], self.broker_a.calls)
        self.assertEqual(
            [("get_binding", ("instance-b", "binding-b"), {})],
            self.broker_b.calls,
        )

    def test_unknown_or_empty_hint_falls_back_to_asking_each_broker(self):
        for query in ("?service_id=unknown", "?service_id="):
            with self.subTest(query=query):
                response = self.client.get("/v2/service_instances/instance-b" + query, headers=self.headers)

                self.assertEqual(HTTPStatus.OK, response.status_code)
                self.assertEqual({"service_id": "service-b", "plan_id": "plan-b"}, response.json)

    def test_without_hint_router_asks_each_broker_in_turn(self):
        response = self.client.get("/v2/service_instances/instance-b", headers=self.headers)

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual([("get_instance", "instance-b", {})], self.broker_a.calls)
        self.assertEqual([("get_instance", "instance-b", {})], self.broker_b.calls)
