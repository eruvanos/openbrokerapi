import http
import json

from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import (
    DeprovisionServiceSpec,
    LastOperation,
    OperationState,
    Service,
    UnbindSpec,
)
from tests import BrokerTestCase

HEADERS = {"X-Broker-Api-Version": "2.17"}
JSON_HEADERS = {**HEADERS, "Content-Type": "application/json"}
BODY = json.dumps({"service_id": "service-guid-here", "plan_id": "plan-guid-here"})
PROVISION_BODY = json.dumps(
    {
        "service_id": "service-guid-here",
        "plan_id": "plan-guid-here",
        "organization_guid": "org-guid-here",
        "space_guid": "space-guid-here",
    }
)
UNKNOWN_PLAN_QUERY = "service_id=service-guid-here&plan_id=OLD-PLAN"


class ErrorMappingTest(BrokerTestCase):
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
        self.headers = {"Authorization": self.auth_header}

    def _calls(self):
        """(name, method that triggers the broker call, mock to set side_effect on)"""
        base = "/v2/service_instances/i1"
        bind = base + "/service_bindings/b1"
        return [
            (
                "provision",
                self.broker.provision,
                lambda: self.client.put(base, data=PROVISION_BODY, headers={**JSON_HEADERS, **self.headers}),
            ),
            (
                "update",
                self.broker.update,
                lambda: self.client.patch(base, data=BODY, headers={**JSON_HEADERS, **self.headers}),
            ),
            (
                "bind",
                self.broker.bind,
                lambda: self.client.put(bind, data=BODY, headers={**JSON_HEADERS, **self.headers}),
            ),
            (
                "unbind",
                self.broker.unbind,
                lambda: self.client.delete(bind + "?" + UNKNOWN_PLAN_QUERY, headers={**HEADERS, **self.headers}),
            ),
            (
                "deprovision",
                self.broker.deprovision,
                lambda: self.client.delete(base + "?" + UNKNOWN_PLAN_QUERY, headers={**HEADERS, **self.headers}),
            ),
        ]

    def test_invalid_parameters_returns_400_on_all_endpoints(self):
        for name, mock, call in self._calls():
            with self.subTest(endpoint=name):
                mock.side_effect = errors.ErrInvalidParameters("bad params")
                response = call()
                self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
                self.assertEqual(response.json, {"error": "InvalidParameters", "description": "bad params"})

    def test_plan_change_not_supported_returns_422(self):
        exc = errors.ErrPlanChangeNotSupported()
        self.broker.update.side_effect = exc
        response = self.client.patch("/v2/service_instances/i1", data=BODY, headers={**JSON_HEADERS, **self.headers})
        self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json, {"description": str(exc)})

    def test_quota_errors_return_422_on_all_endpoints(self):
        for exc in (errors.ErrPlanQuotaExceeded(), errors.ErrServiceQuotaExceeded(), errors.ErrInstanceLimitMet()):
            for name, mock, call in self._calls():
                with self.subTest(endpoint=name, error=type(exc).__name__):
                    mock.side_effect = exc
                    response = call()
                    self.assertEqual(response.status_code, http.HTTPStatus.UNPROCESSABLE_ENTITY)
                    self.assertEqual(response.json, {"description": str(exc)})


class UnknownPlanOnDeleteTest(BrokerTestCase):
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
        self.headers = {**HEADERS, "Authorization": self.auth_header}

    def test_deprovision_with_unknown_plan_reaches_broker(self):
        self.broker.deprovision.return_value = DeprovisionServiceSpec(False)
        response = self.client.delete("/v2/service_instances/i1?" + UNKNOWN_PLAN_QUERY, headers=self.headers)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(self.broker.deprovision.call_args[1]["details"].plan_id, "OLD-PLAN")

    def test_unbind_with_unknown_plan_reaches_broker(self):
        self.broker.unbind.return_value = UnbindSpec(False)
        response = self.client.delete(
            "/v2/service_instances/i1/service_bindings/b1?" + UNKNOWN_PLAN_QUERY, headers=self.headers
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(self.broker.unbind.call_args[1]["details"].plan_id, "OLD-PLAN")

    def test_missing_plan_or_service_id_still_returns_400(self):
        for url in (
            "/v2/service_instances/i1?service_id=s",
            "/v2/service_instances/i1?plan_id=p",
            "/v2/service_instances/i1/service_bindings/b1?service_id=s",
            "/v2/service_instances/i1/service_bindings/b1?plan_id=p",
        ):
            with self.subTest(url=url):
                response = self.client.delete(url, headers=self.headers)
                self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)


class LastBindingOperationErrorsTest(BrokerTestCase):
    URL = "/v2/service_instances/i1/service_bindings/b1/last_operation"

    def setUp(self):
        self.headers = {**HEADERS, "Authorization": self.auth_header}

    def test_binding_not_found_returns_404(self):
        self.broker.last_binding_operation.side_effect = errors.ErrBindingNotFound()
        response = self.client.get(self.URL, headers=self.headers)
        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json, {})

    def test_binding_does_not_exist_returns_410(self):
        self.broker.last_binding_operation.side_effect = errors.ErrBindingDoesNotExist()
        response = self.client.get(self.URL, headers=self.headers)
        self.assertEqual(response.status_code, http.HTTPStatus.GONE)
        self.assertEqual(response.json, {})

    def test_invalid_parameters_returns_400(self):
        self.broker.last_binding_operation.side_effect = errors.ErrInvalidParameters("bad operation")
        response = self.client.get(self.URL, headers=self.headers)
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json, {"error": "InvalidParameters", "description": "bad operation"})

    def test_success_still_returns_200(self):
        self.broker.last_binding_operation.return_value = LastOperation(OperationState.SUCCEEDED, "done")
        response = self.client.get(self.URL, headers=self.headers)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
