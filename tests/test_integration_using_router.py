import json
from http import HTTPStatus
from threading import Thread
from typing import Union, List
from unittest import TestCase
from uuid import uuid4

import requests
from requests.auth import HTTPBasicAuth

import openbrokerapi.auth
from openbrokerapi import api, errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import (
    ServiceBroker,
    Service,
    ProvisionDetails,
    ProvisionedServiceSpec,
    ProvisionState,
    DeprovisionDetails,
    DeprovisionServiceSpec,
    BindDetails,
    Binding,
    BindState,
    UnbindDetails,
    UnbindSpec,
)
from tests import wait_for_port


class FullRouterTestCase(TestCase):
    def setUp(self) -> None:
        broker_username = str(uuid4())
        broker_passsword = str(uuid4())
        self.request_ads = {
            "auth": HTTPBasicAuth(broker_username, broker_passsword),
            "headers": {
                "X-Broker-Api-Version": "2.15",
                "Content-Type": "application/json",
            },
        }

        self.broker_1 = InMemoryBroker(str(uuid4()), str(uuid4()))
        self.broker_2 = InMemoryBroker(str(uuid4()), str(uuid4()))

        def run_server():
            api.serve_multiple(
                [self.broker_1, self.broker_2],
                openbrokerapi.auth.BrokerCredentials(broker_username, broker_passsword),
                host="127.0.0.1",
                port=5002,
            )

        self.server = Thread(target=run_server)
        self.server.setDaemon(True)
        self.server.start()
        wait_for_port(5002, timeout=10)

    def test_lifecycle(self):
        # GIVEN
        org_guid = str(uuid4())
        space_guid = str(uuid4())
        instace_guid = str(uuid4())
        binding_guid = str(uuid4())

        # CATALOG
        self.check_catalog(self.broker_1.service_guid, self.broker_1.plan_guid)
        self.check_catalog(self.broker_2.service_guid, self.broker_2.plan_guid)

        # PROVISION
        self.check_provision(
            instace_guid,
            org_guid,
            space_guid,
            self.broker_1.service_guid,
            self.broker_1.plan_guid,
        )

        # BIND
        self.check_bind(binding_guid, instace_guid)

        # UNBIND
        self.check_unbind(binding_guid, instace_guid)

        # DEPROVISION
        self.check_deprovision(instace_guid)

        # DEPROVISION TWICE
        self.check_deprovision_after_deprovision_done(instace_guid)

    def check_instance_retrievable(self, instace_guid):
        response = requests.get(
            f"http://localhost:5002/v2/service_instances/{instace_guid}",
            **self.request_ads,
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(self.broker_1.service_guid, response.json()["service_id"])
        self.assertEqual(self.broker_1.plan_guid, response.json()["plan_id"])

    def check_unbind(self, binding_guid, instace_guid):
        response = requests.delete(
            f"http://localhost:5002/v2/service_instances/{instace_guid}/service_bindings/{binding_guid}",
            params={
                "service_id": self.broker_1.service_guid,
                "plan_id": self.broker_1.plan_guid,
                "accepts_incomplete": "false",
            },
            **self.request_ads,
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)

    def check_bind(self, binding_guid, instace_guid):
        response = requests.put(
            f"http://localhost:5002/v2/service_instances/{instace_guid}/"
            f"service_bindings/{binding_guid}?accepts_incomplete=false",
            data=json.dumps(
                {
                    "service_id": self.broker_1.service_guid,
                    "plan_id": self.broker_1.plan_guid,
                }
            ),
            **self.request_ads,
        )

        self.assertEqual(HTTPStatus.CREATED, response.status_code)

    def check_deprovision_after_deprovision_done(self, instace_guid):
        response = requests.delete(
            f"http://localhost:5002/v2/service_instances/{instace_guid}",
            params={
                "service_id": self.broker_1.service_guid,
                "plan_id": self.broker_1.plan_guid,
                "accepts_incomplete": "false",
            },
            **self.request_ads,
        )

        self.assertEqual(HTTPStatus.GONE, response.status_code)

    def check_deprovision(self, instace_guid):
        response = requests.delete(
            f"http://localhost:5002/v2/service_instances/{instace_guid}",
            params={
                "service_id": self.broker_1.service_guid,
                "plan_id": self.broker_1.plan_guid,
                "accepts_incomplete": "false",
            },
            **self.request_ads,
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)

    def check_provision(self, instace_guid, org_guid, space_guid, service_guid, plan_guid):
        response = requests.put(
            f"http://localhost:5002/v2/service_instances/{instace_guid}?accepts_incomplete=false",
            data=json.dumps(
                {
                    "organization_guid": org_guid,
                    "space_guid": space_guid,
                    "service_id": service_guid,
                    "plan_id": plan_guid,
                    # "context": {
                    #     "organization_guid": "org-guid-here",
                    #     "space_guid": "space-guid-here",
                    # }
                }
            ),
            **self.request_ads,
        )

        self.assertEqual(HTTPStatus.CREATED, response.status_code)

    def check_catalog(self, service_guid, plan_guid):
        response = requests.get("http://localhost:5002/v2/catalog", **self.request_ads)
        catalog = response.json()
        self.assertEqual(HTTPStatus.OK, response.status_code)
        # find service
        for service in catalog["services"]:
            if service["id"] == service_guid:
                break
        else:
            service = None
        self.assertIsNotNone(service)
        self.assertFalse(service.get("instances_retrievable"))
        self.assertFalse(service.get("bindings_retrievable"))

        # find plan
        for plan in service["plans"]:
            if plan["name"] == "standard":
                break
        else:
            plan = None
        self.assertIsNotNone(plan)
        self.assertEqual(plan_guid, plan.get("id"))


class InMemoryBroker(ServiceBroker):
    CREATED = "CREATED"
    BOUND = "BOUND"
    DELETING = "DELETING"

    def __init__(self, service_guid, plan_guid):
        self.service_guid = service_guid
        self.plan_guid = plan_guid

        self.service_instances = {}

    def catalog(self) -> Union[Service, List[Service]]:
        return Service(
            id=self.service_guid,
            name="InMemService",
            description="InMemService",
            bindable=True,
            plans=[
                ServicePlan(
                    id=self.plan_guid,
                    name="standard",
                    description="standard plan",
                    free=False,
                )
            ],
            instances_retrievable=False,
            bindings_retrievable=False,
        )

    def provision(
        self, instance_id: str, details: ProvisionDetails, async_allowed: bool, **kwargs
    ) -> ProvisionedServiceSpec:
        self.service_instances[instance_id] = {
            "provision_details": details,
            "state": self.CREATED,
        }

        return ProvisionedServiceSpec(state=ProvisionState.SUCCESSFUL_CREATED)

    def bind(
        self,
        instance_id: str,
        binding_id: str,
        details: BindDetails,
        async_allowed: bool,
        **kwargs,
    ) -> Binding:
        instance = self.service_instances.get(instance_id, {})
        if instance and instance.get("state") == self.CREATED:
            instance["state"] = self.BOUND
            return Binding(BindState.SUCCESSFUL_BOUND)

        raise NotImplementedError()

    def unbind(
        self,
        instance_id: str,
        binding_id: str,
        details: UnbindDetails,
        async_allowed: bool,
        **kwargs,
    ) -> UnbindSpec:
        instance = self.service_instances.get(instance_id, {})
        if instance and instance.get("state") == self.BOUND:
            instance["state"] = self.CREATED
            return UnbindSpec(False)

        raise NotImplementedError()

    def deprovision(
        self,
        instance_id: str,
        details: DeprovisionDetails,
        async_allowed: bool,
        **kwargs,
    ) -> DeprovisionServiceSpec:

        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()

        if instance.get("state") == self.CREATED:
            del self.service_instances[instance_id]
            return DeprovisionServiceSpec(False)

        raise NotImplementedError()
