import json

from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import LastOperation, OperationState, Service
from tests import BrokerTestCase

PLAN = "service_id=service-guid-here&plan_id=plan-guid-here"
BODY = json.dumps({"service_id": "service-guid-here", "plan_id": "plan-guid-here"})
PROVISION_BODY = json.dumps(
    {
        "service_id": "service-guid-here",
        "plan_id": "plan-guid-here",
        "organization_guid": "org",
        "space_guid": "space",
    }
)


class InstanceUsableTest(BrokerTestCase):
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
        self.headers = {
            "X-Broker-Api-Version": "2.17",
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }

    def _err(self):
        return errors.ServiceException("boom", instance_usable=False, update_repeatable=False)

    # async last_operation
    def test_last_operation_passes_flags(self):
        self.broker.last_operation.return_value = LastOperation(
            OperationState.FAILED, "x", instance_usable=False, update_repeatable=True
        )
        r = self.client.get(f"/v2/service_instances/i/last_operation?{PLAN}", headers=self.headers)
        self.assertEqual(
            r.json, {"state": "failed", "description": "x", "instance_usable": False, "update_repeatable": True}
        )

    def test_last_operation_omits_flags_by_default(self):
        self.broker.last_operation.return_value = LastOperation(OperationState.FAILED, "x")
        r = self.client.get(f"/v2/service_instances/i/last_operation?{PLAN}", headers=self.headers)
        self.assertEqual(r.json, {"state": "failed", "description": "x"})

    # sync errors
    def test_update_error_includes_both_flags(self):
        self.broker.update.side_effect = self._err()
        r = self.client.patch("/v2/service_instances/i", data=BODY, headers=self.headers)
        self.assertEqual(r.status_code, 500)
        self.assertFalse(r.json["instance_usable"])
        self.assertFalse(r.json["update_repeatable"])

    def test_update_specific_error_includes_flags(self):
        self.broker.update.side_effect = errors.ErrPlanChangeNotSupported(instance_usable=True, update_repeatable=False)
        r = self.client.patch("/v2/service_instances/i", data=BODY, headers=self.headers)
        self.assertEqual(r.status_code, 422)
        self.assertTrue(r.json["instance_usable"])
        self.assertFalse(r.json["update_repeatable"])

    def test_update_concurrency_error_includes_flags(self):
        self.broker.update.side_effect = errors.ErrConcurrentInstanceAccess(instance_usable=True)
        r = self.client.patch("/v2/service_instances/i", data=BODY, headers=self.headers)
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json["instance_usable"], True)
        self.assertNotIn("update_repeatable", r.json)

    def test_deprovision_error_includes_only_instance_usable(self):
        self.broker.deprovision.side_effect = self._err()
        r = self.client.delete(f"/v2/service_instances/i?{PLAN}", headers=self.headers)
        self.assertEqual(r.status_code, 500)
        self.assertFalse(r.json["instance_usable"])
        self.assertNotIn("update_repeatable", r.json)

    def test_other_endpoints_never_include_flags(self):
        for name, call in {
            "provision": lambda: self.client.put("/v2/service_instances/i", data=PROVISION_BODY, headers=self.headers),
            "bind": lambda: self.client.put(
                "/v2/service_instances/i/service_bindings/b", data=BODY, headers=self.headers
            ),
            "unbind": lambda: self.client.delete(
                f"/v2/service_instances/i/service_bindings/b?{PLAN}", headers=self.headers
            ),
            "last_operation": lambda: self.client.get(
                f"/v2/service_instances/i/last_operation?{PLAN}", headers=self.headers
            ),
        }.items():
            for method in ("provision", "bind", "unbind", "last_operation"):
                getattr(self.broker, method).side_effect = self._err()
            r = call()
            self.assertEqual(r.status_code, 500, name)
            self.assertNotIn("instance_usable", r.json, name)
            self.assertNotIn("update_repeatable", r.json, name)

    def test_errors_without_flags_unchanged(self):
        self.broker.update.side_effect = errors.ErrInvalidParameters("bad")
        r = self.client.patch("/v2/service_instances/i", data=BODY, headers=self.headers)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json, {"error": "InvalidParameters", "description": "bad"})

    def test_exception_args_backward_compatible(self):
        self.assertEqual(str(errors.ServiceException("msg")), "msg")
        self.assertIsNone(errors.ServiceException().instance_usable)
