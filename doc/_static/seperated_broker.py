from typing import Union, List

import openbrokerapi
from openbrokerapi.api import ServiceBroker
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.service_broker import (
    Service,
    ProvisionDetails,
    ProvisionedServiceSpec,
    DeprovisionDetails,
    DeprovisionServiceSpec
)


class MyServiceBroker1(ServiceBroker):
    def catalog(self) -> Union[Service, List[Service]]:
        return Service(
            id='service id 1',
            name='service name 1',
            description='service description 1',
            bindable=False,
            plans=[
                ServicePlan(
                    id='plan id',
                    name='plan name',
                    description='plan description',
                )
            ]
        )

    def provision(self,
                  instance_id: str,
                  details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        # Create service instance
        # ...

        return ProvisionedServiceSpec()

    def deprovision(self,
                    instance_id: str,
                    details: DeprovisionDetails,
                    async_allowed: bool) -> DeprovisionServiceSpec:
        # Delete service instance
        # ...

        return DeprovisionServiceSpec(is_async=False)


class MyServiceBroker2(ServiceBroker):
    def catalog(self) -> Union[Service, List[Service]]:
        return Service(
            id='service id 2',
            name='service name 2',
            description='service description 2',
            bindable=False,
            plans=[
                ServicePlan(
                    id='plan id',
                    name='plan name',
                    description='plan description',
                )
            ]
        )

    def provision(self,
                  instance_id: str,
                  details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        # Create service instance
        # ...

        return ProvisionedServiceSpec()

    def deprovision(self,
                    instance_id: str,
                    details: DeprovisionDetails,
                    async_allowed: bool) -> DeprovisionServiceSpec:
        # Delete service instance
        # ...

        return DeprovisionServiceSpec(is_async=False)


openbrokerapi.api.serve_multiple([MyServiceBroker1(), MyServiceBroker2()], None)

# Behind the scenes
# router = Router(MyServiceBroker1(), MyServiceBroker2())
# openbrokerapi.api.serve(router, None)
