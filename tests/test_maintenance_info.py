import http
import json

from openbrokerapi import errors
from openbrokerapi.catalog import MaintenanceInfo, ServicePlan
from openbrokerapi.helper import _to_dict
from openbrokerapi.service_broker import (
    PreviousValues,
    ProvisionDetails,
    ProvisionedServiceSpec,
    Service,
    UpdateDetails,
    UpdateServiceSpec,
)
from tests import BrokerTestCase

HEADERS = {"X-Broker-Api-Version": "2.15", "Content-Type": "application/json"}


class MaintenanceInfoModelTest(BrokerTestCase):
    def test_serialization_drops_none(self):
        self.assertEqual(_to_dict(MaintenanceInfo("1.0")), {"version": "1.0"})
        self.assertEqual(
            _to_dict(MaintenanceInfo("1.0", "desc", extra=1)),
            {"version": "1.0", "description": "desc", "extra": 1},
        )

    def test_plan_serializes_dict_and_model(self):
        for mi in ({"version": "2.0", "description": "d"}, MaintenanceInfo("2.0", "d")):
            plan = ServicePlan("p", "n", "d", maintenance_info=mi)
            self.assertEqual(_to_dict(plan)["maintenance_info"], {"version": "2.0", "description": "d"})

    def test_details_without_maintenance_info(self):
        self.assertIsNone(ProvisionDetails("s", "p", "o", "sp").maintenance_info)
        self.assertIsNone(UpdateDetails("s").maintenance_info)
        self.assertIsNone(PreviousValues().maintenance_info)

    def test_positional_construction_unchanged(self):
        d = ProvisionDetails("s", "p", "o", "sp", {"a": 1}, None)
        self.assertEqual(d.parameters, {"a": 1})
        pv = PreviousValues("p", "s", "o", "sp")
        self.assertEqual((pv.plan_id, pv.space_id), ("p", "sp"))


class MaintenanceInfoApiTest(BrokerTestCase):
    def setUp(self):
        self.broker.catalog.return_value = [
            Service(
                id="service-guid-here",
                name="",
                description="",
                bindable=True,
                plans=[ServicePlan("plan-guid-here", name="", description="", maintenance_info={"version": "1.0.0"})],
            )
        ]

    def _headers(self):
        return {**HEADERS, "Authorization": self.auth_header}

    def _provision(self, extra=None):
        body = {
            "service_id": "service-guid-here",
            "plan_id": "plan-guid-here",
            "organization_guid": "org",
            "space_guid": "space",
        }
        body.update(extra or {})
        return self.client.put("/v2/service_instances/iid", data=json.dumps(body), headers=self._headers())

    def _update(self, extra=None):
        body = {"service_id": "service-guid-here", "plan_id": "plan-guid-here"}
        body.update(extra or {})
        return self.client.patch("/v2/service_instances/iid", data=json.dumps(body), headers=self._headers())

    def test_catalog_contains_maintenance_info(self):
        resp = self.client.get("/v2/catalog", headers=self._headers())
        plan = json.loads(resp.data)["services"][0]["plans"][0]
        self.assertEqual(plan["maintenance_info"], {"version": "1.0.0"})

    def test_provision_receives_maintenance_info(self):
        self.broker.provision.return_value = ProvisionedServiceSpec()
        resp = self._provision({"maintenance_info": {"version": "1.0.0", "description": "x"}})
        self.assertEqual(resp.status_code, http.HTTPStatus.CREATED)
        details = self.broker.provision.call_args[1]["details"]
        self.assertIsInstance(details.maintenance_info, MaintenanceInfo)
        self.assertEqual(details.maintenance_info.version, "1.0.0")
        self.assertEqual(details.maintenance_info.description, "x")

    def test_provision_without_maintenance_info(self):
        self.broker.provision.return_value = ProvisionedServiceSpec()
        self._provision()
        self.assertIsNone(self.broker.provision.call_args[1]["details"].maintenance_info)

    def test_update_receives_maintenance_info_and_previous_values(self):
        self.broker.update.return_value = UpdateServiceSpec(False)
        resp = self._update(
            {
                "maintenance_info": {"version": "2.0.0"},
                "previous_values": {"plan_id": "old", "maintenance_info": {"version": "1.0.0"}},
            }
        )
        self.assertEqual(resp.status_code, http.HTTPStatus.OK)
        details = self.broker.update.call_args[1]["details"]
        self.assertEqual(details.maintenance_info.version, "2.0.0")
        self.assertEqual(details.previous_values.maintenance_info.version, "1.0.0")

    def test_update_without_maintenance_info(self):
        self.broker.update.return_value = UpdateServiceSpec(False)
        self._update({"previous_values": {"plan_id": "old"}})
        details = self.broker.update.call_args[1]["details"]
        self.assertIsNone(details.maintenance_info)
        self.assertIsNone(details.previous_values.maintenance_info)

    def test_provision_conflict_returns_422(self):
        self.broker.provision.side_effect = errors.ErrMaintenanceInfoConflict("changed")
        resp = self._provision({"maintenance_info": {"version": "0.9"}})
        self.assertEqual(resp.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(json.loads(resp.data), {"error": "MaintenanceInfoConflict", "description": "changed"})

    def test_update_conflict_returns_422(self):
        self.broker.update.side_effect = errors.ErrMaintenanceInfoConflict()
        resp = self._update({"maintenance_info": {"version": "0.9"}})
        self.assertEqual(resp.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        body = json.loads(resp.data)
        self.assertEqual(body["error"], "MaintenanceInfoConflict")
        self.assertTrue(body["description"])
