from typing import List

from cfbrokerapi.catalog import Service


class ProvisionDetails:
    def __init__(self,
                 service_id: str,
                 plan_id: str,
                 organization_guid: str,
                 space_guid: str,
                 parameters: dict):
        self.service_id = service_id
        self.plan_id = plan_id
        self.organization_guid = organization_guid
        self.space_guid = space_guid
        self.parameters = parameters


class ProvisionedServiceSpec:
    def __init__(self,
                 is_async: bool,
                 dashboard_url: str,
                 operation_data: str
                 ):
        self.is_async = is_async
        self.dashboard_url = dashboard_url
        self.operation_data = operation_data


class DeprovisionDetails:
    def __init__(self,
                 plan_id: str,
                 service_id: str
                 ):
        self.plan_id = plan_id
        self.service_id = service_id


class DeprovisionServiceSpec:
    def __init__(self,
                 is_async: str,
                 operation_data: str
                 ):
        self.is_async = is_async
        self.operation_data = operation_data


class UpdateDetails:
    def __init__(self,
                 service_id: str,
                 plan_id: str,
                 parameters: str,
                 previous_values: str
                 ):
        self.service_id = service_id
        self.plan_id = plan_id
        self.parameters = parameters
        self.previous_values = previous_values


class UpdateServiceSpec:
    def __init__(self,
                 is_async: bool,
                 operation_data: str):
        self.is_async = is_async
        self.operation_data = operation_data


class ServiceBroker:
    def catalog(self) -> List[Service]:
        raise NotImplementedError()

    def provision(self, instance_id: str, service_details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        raise NotImplementedError()

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
        raise NotImplementedError()

    def deprovision(self, instance_id: str, details: DeprovisionDetails, async_allowed: bool) -> DeprovisionServiceSpec:
        raise NotImplementedError()

        # def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        #     raise NotImplementedError()
        #
        # def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        #     raise NotImplementedError()
