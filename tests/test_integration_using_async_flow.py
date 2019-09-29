import json
import time
from http import HTTPStatus
from threading import Thread
from typing import Union, List, Optional
from unittest import TestCase
from uuid import uuid4

import requests
from requests.auth import HTTPBasicAuth

from openbrokerapi import api, errors
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import (
    ServiceBroker,
    Service,
    ProvisionDetails,
    ProvisionedServiceSpec,
    ProvisionState,
    LastOperation,
    OperationState,
    DeprovisionDetails,
    DeprovisionServiceSpec,
    BindDetails,
    Binding,
    BindState,
    UnbindDetails,
    UnbindSpec,
    GetInstanceDetailsSpec,
    GetBindingSpec)


class FullBrokerTestCase(TestCase):

    def setUp(self) -> None:
        broker_username = str(uuid4())
        broker_passsword = str(uuid4())
        self.request_ads = {
            'auth': HTTPBasicAuth(broker_username, broker_passsword),
            'headers': {'X-Broker-Api-Version': '2.15', 'Content-Type': 'application/json'}
        }

        self.service_guid = str(uuid4())
        self.plan_guid = str(uuid4())
        self.broker = InMemoryBroker(self.service_guid, self.plan_guid)

        def run_server():
            api.serve(self.broker, api.BrokerCredentials(broker_username, broker_passsword), port=5001)

        # self.server = Process(target=run_server)
        self.server = Thread(target=run_server)
        self.server.setDaemon(True)
        self.server.start()
        time.sleep(2)

    def test_lifecycle(self):
        # GIVEN
        org_guid = str(uuid4())
        space_guid = str(uuid4())
        instace_guid = str(uuid4())
        binding_guid = str(uuid4())

        # CATALOG
        self.check_catalog(self.service_guid, self.plan_guid)

        # ASYNC PROVISION
        operation = self.check_provision(instace_guid, org_guid, space_guid, self.service_guid, self.plan_guid)
        self.check_last_operation_after_provision(instace_guid, operation)

        # GET INSTANCE
        self.check_instance_retrievable(instace_guid)

        # ASYNC BIND
        operation = self.check_bind(binding_guid, instace_guid)
        self.check_last_operation_after_bind(binding_guid, instace_guid, operation)

        # GET BINDING
        response = requests.get(
            "http://localhost:5001/v2/service_instances/{}/service_bindings/{}".format(instace_guid, binding_guid),
            **self.request_ads)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertDictEqual({}, response.json())

        # ASYNC UNBIND
        operation = self.check_unbind(binding_guid, instace_guid)
        self.check_last_operation_after_unbind(binding_guid, instace_guid, operation)

        # ASYNC DEPROVISION
        operation = self.check_deprovision(instace_guid, operation)
        self.check_last_operation_after_deprovision(instace_guid, operation)

        # DEPROVISION TWICE
        self.check_deprovision_after_deprovision_done(instace_guid)

    def check_instance_retrievable(self, instace_guid):
        response = requests.get(
            "http://localhost:5001/v2/service_instances/{}".format(instace_guid), **self.request_ads)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(self.service_guid, response.json()['service_id'])
        self.assertEqual(self.plan_guid, response.json()['plan_id'])

    def check_unbind(self, binding_guid, instace_guid):
        response = requests.delete(
            "http://localhost:5001/v2/service_instances/{}/service_bindings/{}".format(instace_guid, binding_guid),
            params={
                "service_id": self.service_guid,
                "plan_id": self.plan_guid,
                'accepts_incomplete': 'true'
            },
            **self.request_ads
        )
        self.assertEqual(HTTPStatus.ACCEPTED, response.status_code)
        operation = response.json().get('operation')
        self.assertEqual('unbind', operation)
        return operation

    def check_last_operation_after_bind(self, binding_guid, instace_guid, operation):
        response = requests.get(
            'http://localhost:5001/v2/service_instances/{}/service_bindings/{}/last_operation'.format(instace_guid,
                                                                                                      binding_guid),
            params={
                'service_id': self.service_guid,
                'plan_id': self.plan_guid,
                'operation': operation,
            },
            **self.request_ads)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual('succeeded', response.json()['state'])

    def check_last_operation_after_unbind(self, binding_guid, instace_guid, operation):
        response = requests.get(
            'http://localhost:5001/v2/service_instances/{}/service_bindings/{}/last_operation'.format(instace_guid,
                                                                                                      binding_guid),
            params={
                'service_id': self.service_guid,
                'plan_id': self.plan_guid,
                'operation': operation,
            },
            **self.request_ads)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual('succeeded', response.json()['state'])

    def check_bind(self, binding_guid, instace_guid):
        response = requests.put(
            "http://localhost:5001/v2/service_instances/{}/service_bindings/{}?accepts_incomplete=true".format(
                instace_guid, binding_guid),
            data=json.dumps({
                "service_id": self.service_guid,
                "plan_id": self.plan_guid
            }),
            **self.request_ads
        )
        self.assertEqual(HTTPStatus.ACCEPTED, response.status_code)
        operation = response.json().get('operation')
        self.assertEqual('bind', operation)
        return operation

    def check_deprovision_after_deprovision_done(self, instace_guid):
        response = requests.delete(
            "http://localhost:5001/v2/service_instances/{}".format(instace_guid),
            params={
                'service_id': self.service_guid,
                'plan_id': self.plan_guid,
                'accepts_incomplete': 'true'
            },
            **self.request_ads)
        self.assertEqual(HTTPStatus.GONE, response.status_code)

    def check_deprovision(self, instace_guid, operation):
        response = requests.delete(
            "http://localhost:5001/v2/service_instances/{}".format(instace_guid),
            params={
                'service_id': self.service_guid,
                'plan_id': self.plan_guid,
                'accepts_incomplete': 'true'
            },
            **self.request_ads)
        self.assertEqual(HTTPStatus.ACCEPTED, response.status_code)
        operation = response.json()['operation']
        self.assertEqual('deprovision', operation)
        return operation

    def check_last_operation_after_deprovision(self, instace_guid, operation):
        response = requests.get(
            "http://localhost:5001/v2/service_instances/{}/last_operation".format(instace_guid),
            params={
                'service_id': self.service_guid,
                'plan_id': self.plan_guid,
                'operation': operation
            },
            **self.request_ads)
        self.assertEqual(HTTPStatus.GONE, response.status_code)
        self.assertEqual('succeeded', response.json()['state'])

    def check_last_operation_after_provision(self, instace_guid, operation):
        response = requests.get(
            "http://localhost:5001/v2/service_instances/{}/last_operation".format(instace_guid),
            params={
                'service_id': self.service_guid,
                'plan_id': self.plan_guid,
                'operation': operation
            },
            **self.request_ads)
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual('succeeded', response.json()['state'])

    def check_provision(self, instace_guid, org_guid, space_guid, service_guid, plan_guid):
        response = requests.put(
            "http://localhost:5001/v2/service_instances/{}?accepts_incomplete=true".format(instace_guid),
            data=json.dumps({
                "organization_guid": org_guid,
                "space_guid": space_guid,
                "service_id": service_guid,
                "plan_id": plan_guid,
                # "context": {
                #     "organization_guid": "org-guid-here",
                #     "space_guid": "space-guid-here",
                # }
            }),
            **self.request_ads)
        self.assertEqual(HTTPStatus.ACCEPTED, response.status_code)

        operation = response.json().get('operation')
        self.assertEqual('provision', operation)

        return operation

    def check_catalog(self, service_guid, plan_guid):
        response = requests.get('http://localhost:5001/v2/catalog', **self.request_ads)
        catalog = response.json()
        self.assertEqual(HTTPStatus.OK, response.status_code)
        # find service
        for service in catalog['services']:
            if service['name'] == 'InMemService':
                break
        else:
            service = None
        self.assertIsNotNone(service)
        self.assertEqual(service_guid, service.get('id'))
        self.assertTrue(service.get('instances_retrievable'))
        self.assertTrue(service.get('bindings_retrievable'))

        # find plan
        for plan in service['plans']:
            if plan['name'] == 'standard':
                break
        else:
            plan = None
        self.assertIsNotNone(plan)
        self.assertEqual(plan_guid, plan.get('id'))


class InMemoryBroker(ServiceBroker):
    CREATING = 'CREATING'
    CREATED = 'CREATED'
    BINDING = 'BINDING'
    BOUND = 'BOUND'
    UNBINDING = 'UNBINDING'
    DELETING = 'DELETING'

    def __init__(self, service_guid, plan_guid):
        self.service_guid = service_guid
        self.plan_guid = plan_guid

        self.service_instances = dict()

    def catalog(self) -> Union[Service, List[Service]]:
        return Service(
            id=self.service_guid,
            name='InMemService',
            description='InMemService',
            bindable=True,
            plans=[
                ServicePlan(
                    id=self.plan_guid,
                    name='standard',
                    description='standard plan',
                    free=False,
                )
            ],
            instances_retrievable=True,
            bindings_retrievable=True
        )

    def provision(self,
                  instance_id: str,
                  details: ProvisionDetails,
                  async_allowed: bool,
                  **kwargs) -> ProvisionedServiceSpec:
        if not async_allowed:
            raise errors.ErrAsyncRequired()

        self.service_instances[instance_id] = {
            'provision_details': details,
            'state': self.CREATING
        }

        return ProvisionedServiceSpec(
            state=ProvisionState.IS_ASYNC,
            operation='provision'
        )

    def bind(self, instance_id: str, binding_id: str, details: BindDetails, async_allowed: bool, **kwargs) -> Binding:
        if not async_allowed:
            raise errors.ErrAsyncRequired()

        instance = self.service_instances.get(instance_id, {})
        if instance and instance.get('state') == self.CREATED:
            instance['state'] = self.BINDING
            return Binding(BindState.IS_ASYNC, operation='bind')

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails, async_allowed: bool,
               **kwargs) -> UnbindSpec:
        if not async_allowed:
            raise errors.ErrAsyncRequired()

        instance = self.service_instances.get(instance_id, {})
        if instance and instance.get('state') == self.BOUND:
            instance['state'] = self.UNBINDING
            return UnbindSpec(True, 'unbind')

    def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool,
                    **kwargs) -> DeprovisionServiceSpec:
        if not async_allowed:
            raise errors.ErrAsyncRequired()

        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()

        if instance.get('state') == self.CREATED:
            instance['state'] = self.DELETING
            return DeprovisionServiceSpec(True, 'deprovision')

    def last_operation(self, instance_id: str, operation_data: Optional[str], **kwargs) -> LastOperation:
        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()

        if instance.get('state') == self.CREATING:
            instance['state'] = self.CREATED
            return LastOperation(OperationState.SUCCEEDED)
        elif instance.get('state') == self.DELETING:
            del self.service_instances[instance_id]
            raise errors.ErrInstanceDoesNotExist()

    def last_binding_operation(self,
                               instance_id: str,
                               binding_id: str,
                               operation_data: Optional[str],
                               **kwargs
                               ) -> LastOperation:
        instance = self.service_instances.get(instance_id, {})
        if instance.get('state') == self.BINDING:
            instance['state'] = self.BOUND
            return LastOperation(OperationState.SUCCEEDED)
        elif instance.get('state') == self.UNBINDING:
            instance['state'] = self.CREATED
            return LastOperation(OperationState.SUCCEEDED)

    def get_instance(self, instance_id: str, **kwargs) -> GetInstanceDetailsSpec:
        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()

        return GetInstanceDetailsSpec(
            self.service_guid,
            self.plan_guid
        )

    def get_binding(self, instance_id: str, binding_id: str, **kwargs) -> GetBindingSpec:
        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()

        if instance.get('state') == self.BOUND:
            return GetBindingSpec()
