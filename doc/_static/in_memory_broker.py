from typing import Union, List

import openbrokerapi
from openbrokerapi import errors
from openbrokerapi.api import ServiceBroker
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import (
    Service,
    ProvisionDetails,
    ProvisionedServiceSpec,
    DeprovisionDetails,
    DeprovisionServiceSpec,
    ProvisionState,
    Binding,
    BindState,
    UnbindDetails,
    UnbindSpec,
    BindDetails,
)


class InMemoryBroker(ServiceBroker):
    CREATING = "CREATING"
    CREATED = "CREATED"
    BINDING = "BINDING"
    BOUND = "BOUND"
    UNBINDING = "UNBINDING"
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
        )

    def provision(
        self, instance_id: str, details: ProvisionDetails, async_allowed: bool, **kwargs
    ) -> ProvisionedServiceSpec:
        if not async_allowed:
            raise errors.ErrAsyncRequired()

        self.service_instances[instance_id] = {
            "provision_details": details,
            "state": self.CREATING,
        }

        return ProvisionedServiceSpec(state=ProvisionState.IS_ASYNC, operation="provision")

    def bind(self, instance_id: str, binding_id: str, details: BindDetails, async_allowed: bool, **kwargs) -> Binding:
        instance = self.service_instances.get(instance_id, {})
        if instance and instance.get("state") == self.CREATED:
            instance["state"] = self.BOUND
            return Binding(BindState.SUCCESSFUL_BOUND)

    def unbind(
        self, instance_id: str, binding_id: str, details: UnbindDetails, async_allowed: bool, **kwargs
    ) -> UnbindSpec:
        instance = self.service_instances.get(instance_id, {})
        if instance and instance.get("state") == self.BOUND:
            instance["state"] = self.CREATED
            return UnbindSpec(False)

    def deprovision(
        self, instance_id: str, details: DeprovisionDetails, async_allowed: bool, **kwargs
    ) -> DeprovisionServiceSpec:
        instance = self.service_instances.get(instance_id)
        if instance is None:
            raise errors.ErrInstanceDoesNotExist()

        if instance.get("state") == self.CREATED:
            del self.service_instances[instance_id]
            return DeprovisionServiceSpec(False)


openbrokerapi.api.serve(InMemoryBroker("service-guid", "plan-guid"), None)
