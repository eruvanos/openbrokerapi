import unittest
from unittest.mock import Mock
from uuid import uuid4

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
    UnbindDetails,
    UpdateDetails,
    UpdateServiceSpec,
    LastOperation,
    OperationState)


class RouterTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.b1 = Mock()
        self.s1 = Service(id='s1', name='s1', description='s1', bindable=True,
                          plans=[ServicePlan('p1', name='', description='')])
        self.b1.catalog.return_value = [self.s1]

        self.b2 = Mock()
        self.s2 = Service(id='s2', name='s2', description='s2', bindable=True,
                          plans=[ServicePlan('p2', name='', description='')])
        self.b2.catalog.return_value = [self.s2]

        self.router = Router(self.b1, self.b2)

    def test_router_combines_catalogs(self):
        catalog = self.router.catalog()

        self.assertListEqual([self.s1, self.s2], catalog)

    def test_routes_provision(self):
        operation_str = str(uuid4())
        self.b1.provision.return_value = ProvisionedServiceSpec(state=ProvisionState.IS_ASYNC,
                                                                dashboard_url="dash_url",
                                                                operation=operation_str)

        provision = self.router.provision(str(uuid4()), ProvisionDetails('s1', 'p1', str(uuid4()), str(uuid4())), True)

        self.assertEqual('s1 ' + operation_str, provision.operation)
        self.assertTrue(self.b1.provision.called)

    def test_routes_bind(self):
        self.b1.bind.return_value = Binding()

        _ = self.router.bind(str(uuid4()), str(uuid4()), BindDetails('s1', 'p1'))

        self.assertTrue(self.b1.bind.called)

    def test_routes_update(self):
        operation_str = str(uuid4())
        self.b1.update.return_value = UpdateServiceSpec(is_async=True, operation=operation_str)

        update = self.router.update(str(uuid4()), UpdateDetails('s1', 'p1'), True)

        self.assertEqual('s1 ' + operation_str, update.operation)
        self.assertTrue(self.b1.update.called)

    def test_routes_unbind(self):
        self.b1.unbind.return_value = None

        _ = self.router.unbind(str(uuid4()), str(uuid4()), UnbindDetails('s1', 'p1'))

        self.assertTrue(self.b1.unbind.called)

    def test_routes_deprovision(self):
        operation_str = str(uuid4())
        self.b1.deprovision.return_value = DeprovisionServiceSpec(is_async=True, operation=operation_str)

        deprovision = self.router.deprovision(str(uuid4()), DeprovisionDetails('s1', 'p1'), True)

        self.assertEqual('s1 ' + operation_str, deprovision.operation)
        self.assertTrue(self.b1.deprovision.called)

    def test_routes_last_operation(self):
        instance_id = str(uuid4())
        operation_str = str(uuid4())
        self.b1.last_operation.return_value = LastOperation(state=OperationState.IN_PROGRESS)

        _ = self.router.last_operation(instance_id, 's1 ' + operation_str)

        self.b1.last_operation.assert_called_with(instance_id, operation_str)


if __name__ == '__main__':
    unittest.main()
