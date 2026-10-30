import json
from http import HTTPStatus

from openbrokerapi.catalog import MaintenanceInfo, ServicePlan
from openbrokerapi.response import GetInstanceResponse, ProvisioningResponse, UpdateResponse
from openbrokerapi.service_broker import (
    GetInstanceDetailsSpec,
    ProvisionedServiceSpec,
    ProvisionState,
    Service,
    ServiceInstanceMetadata,
    UpdateServiceSpec,
)
from tests import BrokerTestCase

HEADERS = {"X-Broker-Api-Version": "2.17", "Content-Type": "application/json"}


class InstanceMetadataTest(BrokerTestCase):
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
        self.metadata = ServiceInstanceMetadata(labels={"k": "v"}, attributes={"a": "b"})
        self.expected = {"labels": {"k": "v"}, "attributes": {"a": "b"}}

    def _headers(self):
        return {**HEADERS, "Authorization": self.auth_header}

    def _provision(self, query=""):
        return self.client.put(
            "/v2/service_instances/iid" + query,
            data=json.dumps(
                {
                    "service_id": "service-guid-here",
                    "plan_id": "plan-guid-here",
                    "organization_guid": "org",
                    "space_guid": "space",
                }
            ),
            headers=self._headers(),
        )

    def _update(self, query=""):
        return self.client.patch(
            "/v2/service_instances/iid" + query,
            data=json.dumps({"service_id": "service-guid-here", "plan_id": "plan-guid-here"}),
            headers=self._headers(),
        )

    def test_model_defaults_and_extra_kwargs(self):
        m = ServiceInstanceMetadata()
        self.assertIsNone(m.labels)
        self.assertIsNone(m.attributes)
        self.assertEqual("x", ServiceInstanceMetadata(custom="x").custom)

    def test_provision_created_has_metadata(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(metadata=self.metadata)
        r = self._provision()
        self.assertEqual(HTTPStatus.CREATED, r.status_code)
        self.assertEqual(self.expected, r.json["metadata"])

    def test_provision_async_has_metadata(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(
            ProvisionState.IS_ASYNC, "http://dash", "op", self.metadata
        )
        r = self._provision("?accepts_incomplete=true")
        self.assertEqual(HTTPStatus.ACCEPTED, r.status_code)
        self.assertEqual(self.expected, r.json["metadata"])
        self.assertEqual("op", r.json["operation"])

    def test_provision_identical_has_metadata(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(
            ProvisionState.IDENTICAL_ALREADY_EXISTS, metadata=self.metadata
        )
        r = self._provision()
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(self.expected, r.json["metadata"])

    def test_provision_without_metadata_unchanged(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(dashboard_url="http://dash")
        r = self._provision()
        self.assertEqual({"dashboard_url": "http://dash"}, r.json)

    def test_partial_metadata_omits_unset_parts(self):
        self.broker.provision.return_value = ProvisionedServiceSpec(metadata=ServiceInstanceMetadata(labels={"k": "v"}))
        r = self._provision()
        self.assertEqual({"labels": {"k": "v"}}, r.json["metadata"])

    def test_update_sync_has_metadata(self):
        self.broker.update.return_value = UpdateServiceSpec(False, metadata=self.metadata)
        r = self._update()
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(self.expected, r.json["metadata"])

    def test_update_async_has_metadata(self):
        self.broker.update.return_value = UpdateServiceSpec(True, "op", metadata=self.metadata)
        r = self._update("?accepts_incomplete=true")
        self.assertEqual(HTTPStatus.ACCEPTED, r.status_code)
        self.assertEqual(self.expected, r.json["metadata"])

    def test_update_without_metadata_unchanged(self):
        self.broker.update.return_value = UpdateServiceSpec(False, dashboard_url="http://dash")
        r = self._update()
        self.assertEqual({"dashboard_url": "http://dash"}, r.json)

    def test_get_instance_with_metadata_and_maintenance_info(self):
        self.broker.get_instance.return_value = GetInstanceDetailsSpec(
            "service-guid-here",
            "plan-guid-here",
            metadata=self.metadata,
            maintenance_info=MaintenanceInfo("1.2.3", "desc"),
        )
        r = self.client.get("/v2/service_instances/iid", headers=self._headers())
        self.assertEqual(HTTPStatus.OK, r.status_code)
        self.assertEqual(self.expected, r.json["metadata"])
        self.assertEqual({"version": "1.2.3", "description": "desc"}, r.json["maintenance_info"])

    def test_get_instance_without_new_fields_unchanged(self):
        self.broker.get_instance.return_value = GetInstanceDetailsSpec("service-guid-here", "plan-guid-here")
        r = self.client.get("/v2/service_instances/iid", headers=self._headers())
        self.assertEqual({"service_id": "service-guid-here", "plan_id": "plan-guid-here"}, r.json)

    def test_positional_construction_still_works(self):
        spec = GetInstanceDetailsSpec("s", "p", "http://d", {"a": 1})
        self.assertEqual({"a": 1}, spec.parameters)
        self.assertIsNone(spec.metadata)
        self.assertIsNone(spec.maintenance_info)
        self.assertIsNone(ProvisionedServiceSpec(ProvisionState.IS_ASYNC, "d", "o").metadata)
        self.assertIsNone(UpdateServiceSpec(True, "o", "d").metadata)
        self.assertIsNone(ProvisioningResponse("d", "o").metadata)
        self.assertIsNone(UpdateResponse("o", "d").metadata)
        self.assertIsNone(GetInstanceResponse("s", "p", "d", {}).metadata)
