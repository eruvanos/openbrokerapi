import unittest
from unittest.mock import Mock
from uuid import uuid4

from openbrokerapi import errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.router import Router
from openbrokerapi.service_broker import (
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
    GetInstanceDetailsSpec,
    GetBindingSpec,
    UpdateDetails,
    UpdateServiceSpec,
    LastOperation,
    OperationState,
)


class RouterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.b1 = Mock()
        self.s1 = Service(
            id="s1",
            name="s1",
            description="s1",
            bindable=True,
            plans=[ServicePlan("p1", name="", description="")],
        )
        self.b1.catalog.return_value = [self.s1]

        self.b2 = Mock()
        self.s2 = Service(
            id="s2",
            name="s2",
            description="s2",
            bindable=True,
            plans=[ServicePlan("p2", name="", description="")],
        )
        self.b2.catalog.return_value = [self.s2]

        self.router = Router(self.b1, self.b2)

    def test_router_combines_catalogs(self):
        catalog = self.router.catalog()

        self.assertListEqual([self.s1, self.s2], catalog)

    def test_routes_provision(self):
        operation_str = str(uuid4())
        self.b1.provision.return_value = ProvisionedServiceSpec(
            state=ProvisionState.IS_ASYNC,
            dashboard_url="dash_url",
            operation=operation_str,
        )

        provision = self.router.provision(str(uuid4()), ProvisionDetails("s1", "p1", str(uuid4()), str(uuid4())), True)

        self.assertEqual("s1 " + operation_str, provision.operation)
        self.assertTrue(self.b1.provision.called)

    def test_routes_bind_and_passes_async_allowed(self):
        for async_allowed in (True, False):
            with self.subTest(async_allowed=async_allowed):
                self.b1.bind.reset_mock()
                self.b1.bind.return_value = Binding()
                instace_guid = str(uuid4())
                binding_id = str(uuid4())
                bind_details = BindDetails("s1", "p1")

                binding = self.router.bind(instace_guid, binding_id, bind_details, async_allowed)

                self.b1.bind.assert_called_once_with(instace_guid, binding_id, bind_details, async_allowed)
                self.assertIsNone(binding.operation)

    def test_routes_async_bind_adds_service_id_to_operation(self):
        operation_str = str(uuid4())
        self.b2.bind.return_value = Binding(state=BindState.IS_ASYNC, operation=operation_str)

        binding = self.router.bind(str(uuid4()), str(uuid4()), BindDetails("s2", "p2"), True)

        self.assertEqual("s2 " + operation_str, binding.operation)
        self.assertFalse(self.b1.bind.called)

    def test_routes_update(self):
        operation_str = str(uuid4())
        self.b1.update.return_value = UpdateServiceSpec(is_async=True, operation=operation_str)

        update = self.router.update(str(uuid4()), UpdateDetails("s1", "p1"), True)

        self.assertEqual("s1 " + operation_str, update.operation)
        self.assertTrue(self.b1.update.called)

    def test_routes_unbind_and_passes_async_allowed(self):
        for async_allowed in (True, False):
            with self.subTest(async_allowed=async_allowed):
                self.b1.unbind.reset_mock()
                self.b1.unbind.return_value = UnbindSpec(is_async=False)
                instace_guid = str(uuid4())
                binding_id = str(uuid4())
                unbind_details = UnbindDetails("s1", "p1")

                _ = self.router.unbind(instace_guid, binding_id, unbind_details, async_allowed)

                self.b1.unbind.assert_called_once_with(instace_guid, binding_id, unbind_details, async_allowed)

    def test_routes_async_unbind_adds_service_id_to_operation(self):
        operation_str = str(uuid4())
        self.b1.unbind.return_value = UnbindSpec(is_async=True, operation=operation_str)

        unbind = self.router.unbind(str(uuid4()), str(uuid4()), UnbindDetails("s1", "p1"), True)

        self.assertEqual("s1 " + operation_str, unbind.operation)

    def test_routes_deprovision(self):
        operation_str = str(uuid4())
        self.b1.deprovision.return_value = DeprovisionServiceSpec(is_async=True, operation=operation_str)

        deprovision = self.router.deprovision(str(uuid4()), DeprovisionDetails("s1", "p1"), True)

        self.assertEqual("s1 " + operation_str, deprovision.operation)
        self.assertTrue(self.b1.deprovision.called)

    def test_routes_last_operation(self):
        instance_id = str(uuid4())
        operation_str = str(uuid4())
        self.b1.last_operation.return_value = LastOperation(state=OperationState.IN_PROGRESS)

        _ = self.router.last_operation(instance_id, "s1 " + operation_str, service_id="s1", plan_id="p1")

        self.b1.last_operation.assert_called_with(instance_id, operation_str, service_id="s1", plan_id="p1")

    def test_routes_last_operation_without_provider_operation(self):
        instance_id = str(uuid4())
        self.b2.last_operation.return_value = LastOperation(state=OperationState.SUCCEEDED)

        _ = self.router.last_operation(instance_id, "s2")

        self.b2.last_operation.assert_called_with(instance_id, None, service_id=None, plan_id=None)

    def test_last_operation_rejects_missing_or_unknown_operation(self):
        for operation in (None, "unknown op"):
            with self.subTest(operation=operation):
                with self.assertRaises(errors.ErrInvalidParameters):
                    self.router.last_operation(str(uuid4()), operation)

    def test_routes_last_binding_operation(self):
        instance_id = str(uuid4())
        binding_id = str(uuid4())
        operation_str = str(uuid4())
        self.b2.last_binding_operation.return_value = LastOperation(state=OperationState.IN_PROGRESS)

        _ = self.router.last_binding_operation(
            instance_id, binding_id, "s2 " + operation_str, service_id="s2", plan_id="p2"
        )

        self.b2.last_binding_operation.assert_called_with(
            instance_id, binding_id, operation_str, service_id="s2", plan_id="p2"
        )
        self.assertFalse(self.b1.last_binding_operation.called)

    def test_last_binding_operation_rejects_missing_or_unknown_operation(self):
        for operation in (None, "unknown op"):
            with self.subTest(operation=operation):
                with self.assertRaises(errors.ErrInvalidParameters):
                    self.router.last_binding_operation(str(uuid4()), str(uuid4()), operation)

    def test_get_instance_routes_on_service_id_hint(self):
        spec = GetInstanceDetailsSpec("s2", "p2")
        self.b2.get_instance.return_value = spec

        result = self.router.get_instance("i1", service_id="s2", plan_id="p2")

        self.assertIs(spec, result)
        self.b2.get_instance.assert_called_once_with("i1", service_id="s2", plan_id="p2")
        self.assertFalse(self.b1.get_instance.called)

    def test_get_instance_with_unknown_service_id_hint_does_not_exist(self):
        with self.assertRaises(errors.ErrInstanceDoesNotExist):
            self.router.get_instance("i1", service_id="unknown")

    def test_get_instance_tries_each_provider(self):
        spec = GetInstanceDetailsSpec("s2", "p2")
        self.b1.get_instance.side_effect = errors.ErrInstanceDoesNotExist()
        self.b2.get_instance.return_value = spec

        result = self.router.get_instance("i1")

        self.assertIs(spec, result)
        self.b1.get_instance.assert_called_once_with("i1")
        self.b2.get_instance.assert_called_once_with("i1")

    def test_get_instance_skips_providers_not_implementing_it(self):
        spec = GetInstanceDetailsSpec("s2", "p2")
        self.b1.get_instance.side_effect = NotImplementedError()
        self.b2.get_instance.return_value = spec

        self.assertIs(spec, self.router.get_instance("i1"))

    def test_get_instance_not_found_in_any_provider(self):
        self.b1.get_instance.side_effect = errors.ErrInstanceDoesNotExist()
        self.b2.get_instance.side_effect = NotImplementedError()

        with self.assertRaises(errors.ErrInstanceDoesNotExist):
            self.router.get_instance("i1")

    def test_get_instance_not_implemented_by_any_provider(self):
        self.b1.get_instance.side_effect = NotImplementedError()
        self.b2.get_instance.side_effect = NotImplementedError()

        with self.assertRaises(NotImplementedError):
            self.router.get_instance("i1")

    def test_get_instance_propagates_other_errors(self):
        self.b1.get_instance.side_effect = errors.ErrConcurrentInstanceAccess()

        with self.assertRaises(errors.ErrConcurrentInstanceAccess):
            self.router.get_instance("i1")
        self.assertFalse(self.b2.get_instance.called)

    def test_get_binding_routes_on_service_id_hint(self):
        spec = GetBindingSpec(credentials={"a": "b"})
        self.b1.get_binding.return_value = spec

        result = self.router.get_binding("i1", "b1", service_id="s1")

        self.assertIs(spec, result)
        self.b1.get_binding.assert_called_once_with("i1", "b1", service_id="s1")
        self.assertFalse(self.b2.get_binding.called)

    def test_get_binding_tries_each_provider(self):
        spec = GetBindingSpec(credentials={"a": "b"})
        self.b1.get_binding.side_effect = errors.ErrBindingDoesNotExist()
        self.b2.get_binding.return_value = spec

        self.assertIs(spec, self.router.get_binding("i1", "b1"))

    def test_get_binding_not_found_in_any_provider(self):
        self.b1.get_binding.side_effect = errors.ErrBindingDoesNotExist()
        self.b2.get_binding.side_effect = errors.ErrBindingDoesNotExist()

        with self.assertRaises(errors.ErrBindingDoesNotExist):
            self.router.get_binding("i1", "b1")


if __name__ == "__main__":
    unittest.main()
