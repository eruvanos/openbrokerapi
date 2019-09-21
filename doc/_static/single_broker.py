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


class MyServiceBroker(ServiceBroker):
    def catalog(self) -> Union[Service, List[Service]]:
        return Service(
            id='service id',
            name='service name',
            description='service description',
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


openbrokerapi.api.serve(MyServiceBroker(), None)
