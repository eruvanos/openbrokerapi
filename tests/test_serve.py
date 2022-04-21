import time
from multiprocessing import Process
from unittest import TestCase
from unittest.mock import Mock

import requests

from openbrokerapi import api
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import (
    Service,
    ProvisionedServiceSpec,
    ServiceBroker,
    DeprovisionDetails,
    DeprovisionServiceSpec,
    ProvisionDetails,
)


class InMemBroker(ServiceBroker):
    instances = dict()

    def __init__(self, service_guid="service-test-guid", plan_guid="plan-test-guid"):
        self.service_guid = service_guid
        self.plan_guid = plan_guid

    def catalog(self) -> Service:
        return Service(
            id=self.service_guid,
            name="TestService",
            description="TestMe",
            bindable=False,
            plans=[
                ServicePlan(id=self.plan_guid, name="TestPlan", description="TestMe")
            ],
        )

    def provision(
        self, instance_id: str, details: ProvisionDetails, async_allowed: bool, **kwargs
    ) -> ProvisionedServiceSpec:
        self.instances[instance_id] = details
        return ProvisionedServiceSpec()

    def deprovision(
        self,
        instance_id: str,
        details: DeprovisionDetails,
        async_allowed: bool,
        **kwargs
    ) -> DeprovisionServiceSpec:
        del self.instances[instance_id]
        return DeprovisionServiceSpec(is_async=False)


def run_serve_provision_without_auth():
    api.serve(InMemBroker(), credentials=None, host="127.0.0.1", port=5001)


def run_serve_starts_server():
    broker = Mock()
    broker.catalog.return_value = []
    api.serve(broker, api.BrokerCredentials("", ""), host="127.0.0.1", port=5001)


def run_serve_starts_server_without_auth():
    broker = Mock()
    broker.catalog.return_value = []
    api.serve(broker, credentials=None, host="127.0.0.1", port=5001)


def run_serve_starts_with_single_instance():
    broker = Mock()
    broker.catalog.return_value = Service("id", "name", "description", False, [])
    api.serve(
        broker,
        [
            api.BrokerCredentials("cfy-login", "cfy-pwd"),
            api.BrokerCredentials("k8s-login", "k8s-pwd"),
        ],
        host="127.0.0.1",
        port=5001,
    )


class ServeTest(TestCase):
    def test_serve_starts_server(self):
        server = Process(target=run_serve_starts_server)
        server.start()

        time.sleep(2)
        response = requests.get(
            "http://localhost:5001/v2/catalog",
            auth=("", ""),
            headers={"X-Broker-Api-Version": "2.13"},
        )
        server.kill()
        server.join()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), dict(services=[]))

    def test_serve_starts_server_without_auth(self):
        server = Process(target=run_serve_starts_server_without_auth)
        server.start()

        time.sleep(2)
        response = requests.get(
            "http://localhost:5001/v2/catalog", headers={"X-Broker-Api-Version": "2.13"}
        )

        server.kill()
        server.join()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), dict(services=[]))

    def test_provision_without_auth(self):
        server = Process(target=run_serve_provision_without_auth)
        server.start()

        time.sleep(2)

        response = requests.put(
            "http://localhost:5001/v2/service_instances/here-instance-id?accepts_incomplete=true",
            json={
                "service_id": "service-test-guid",
                "plan_id": "plan-test-guid",
                "organization_guid": "org-guid-here",
                "space_guid": "space-guid-here",
                "parameters": {"parameter1": 1},
                "context": {
                    "organization_guid": "org-guid-here",
                    "space_guid": "space-guid-here",
                },
            },
            headers={"X-Broker-Api-Version": "2.13"},
        )

        server.kill()
        server.join()

        self.assertEqual(response.status_code, 201)

    def test_serve_starts_with_single_instance(self):
        server = Process(target=run_serve_starts_with_single_instance)
        server.start()

        time.sleep(2)
        response = requests.get(
            "http://localhost:5001/v2/catalog",
            auth=("k8s-login", "k8s-pwd"),
            headers={"X-Broker-Api-Version": "2.13"},
        )
        server.kill()
        server.join()

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            dict(
                services=[
                    {
                        "bindable": False,
                        "description": "description",
                        "id": "id",
                        "name": "name",
                        "instances_retrievable": False,
                        "bindings_retrievable": False,
                        "plan_updateable": False,
                        "plans": [],
                    }
                ]
            ),
        )
