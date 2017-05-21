from typing import List

from cfbrokerapi.catalog import Service


class ProvisionDetails:
    def __init__(self,
                 service_id: str,
                 plan_id: str,
                 organization_guid: str,
                 space_guid: str,
                 parameters=None):
        if parameters is None:
            parameters = {}

        self.service_id = service_id
        self.plan_id = plan_id
        self.organization_guid = organization_guid
        self.space_guid = space_guid
        self.parameters = parameters


class ProvisionedServiceSpec:
    def __init__(self,
                 # is_async: bool,
                 dashboard_url: str,
                 operation: str
                 ):
        self.is_async = False
        self.dashboard_url = dashboard_url
        self.operation = operation


class DeprovisionDetails:
    def __init__(self,
                 plan_id: str,
                 service_id: str
                 ):
        self.plan_id = plan_id
        self.service_id = service_id


class DeprovisionServiceSpec:
    def __init__(self,
                 is_async: bool,
                 operation: str
                 ):
        self.is_async = is_async
        self.operation = operation


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


class BindResource:
    def __init__(self,
                 app_guid: str = None,
                 route: str = None
                 ):
        self.app_guid = app_guid
        self.route = route


class BindDetails:
    def __init__(self,
                 service_id: str,
                 plan_id: str,
                 app_guid: str = None,
                 bind_resource: BindResource = None,
                 parameters: dict= None
                 ):
        self.app_guid = app_guid
        self.plan_id = plan_id
        self.service_id = service_id
        self.bind_resource = bind_resource
        self.parameters = parameters


class SharedDevice:
    def __init__(self,
                 volume_id: str,
                 mount_config: dict
                 ):
        self.volume_id = volume_id
        self.mount_config = mount_config


class VolumeMount:
    def __init__(self,
                 driver: str,
                 container_dir: str,
                 mode: str,
                 device_type: str,
                 device: SharedDevice
                 ):
        self.driver = driver
        self.container_dir = container_dir
        self.mode = mode
        self.device_type = device_type
        self.device = device


class Binding:
    def __init__(self,
                 credentials: dict = None,
                 syslog_drain_url: str = None,
                 route_service_url: str = None,
                 volume_mounts: List[VolumeMount] = None
                 ):
        self.credentials = credentials
        self.syslog_drain_url = syslog_drain_url
        self.route_service_url = route_service_url
        self.volume_mounts = volume_mounts


class UnbindDetails:
    def __init__(self,
                 plan_id: str,
                 service_id: str
                 ):
        self.plan_id = plan_id
        self.service_id = service_id


class ServiceBroker:
    def catalog(self) -> List[Service]:
        raise NotImplementedError()

    def provision(self, instance_id: str, service_details: ProvisionDetails,
                  async_allowed: bool) -> ProvisionedServiceSpec:
        raise NotImplementedError()

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool) -> UpdateServiceSpec:
        raise NotImplementedError()

    def deprovision(self, instance_id: str, details: DeprovisionDetails,
                    async_allowed: bool) -> DeprovisionServiceSpec:
        raise NotImplementedError()

    def bind(self, instance_id: str, binding_id: str, details: BindDetails) -> Binding:
        raise NotImplementedError()

        # def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails):
        #     raise NotImplementedError()
