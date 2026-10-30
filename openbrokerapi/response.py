from typing import List, Optional

from openbrokerapi.catalog import MaintenanceInfo
from openbrokerapi.service_broker import OperationState, ServiceInstanceMetadata, VolumeMount, Service


class EmptyResponse:
    pass


class ErrorResponse:
    def __init__(
        self,
        error: Optional[str] = None,
        description: Optional[str] = None,
        instance_usable: Optional[bool] = None,
        update_repeatable: Optional[bool] = None,
    ):
        self.error = error
        self.description = description
        self.instance_usable = instance_usable
        self.update_repeatable = update_repeatable


class AsyncResponse:
    pass


class CatalogResponse:
    def __init__(self, services: List[Service]):
        self.services = services


class ProvisioningResponse(AsyncResponse):
    def __init__(self, dashboard_url: str, operation: str, metadata: Optional[ServiceInstanceMetadata] = None):
        self.dashboard_url = dashboard_url
        self.operation = operation
        self.metadata = metadata


class GetInstanceResponse:
    def __init__(
        self,
        service_id: str,
        plan_id: str,
        dashboard_url: Optional[str] = None,
        parameters: Optional[dict] = None,
        metadata: Optional[ServiceInstanceMetadata] = None,
        maintenance_info: Optional[MaintenanceInfo] = None,
    ):
        self.service_id = service_id
        self.plan_id = plan_id
        self.dashboard_url = dashboard_url
        self.parameters = parameters
        self.metadata = metadata
        self.maintenance_info = maintenance_info


class BindResponse:
    def __init__(
        self,
        credentials: Optional[dict] = None,
        syslog_drain_url: Optional[str] = None,
        route_service_url: Optional[str] = None,
        volume_mounts: Optional[List[VolumeMount]] = None,
        operation: Optional[str] = None,
    ):
        self.credentials = credentials
        self.syslog_drain_url = syslog_drain_url
        self.route_service_url = route_service_url
        self.volume_mounts = volume_mounts
        self.operation = operation


class GetBindingResponse:
    def __init__(
        self,
        credentials: Optional[dict] = None,
        syslog_drain_url: Optional[str] = None,
        route_service_url: Optional[str] = None,
        volume_mounts: Optional[List[VolumeMount]] = None,
        parameters: Optional[dict] = None,
    ):
        self.credentials = credentials
        self.syslog_drain_url = syslog_drain_url
        self.route_service_url = route_service_url
        self.volume_mounts = volume_mounts
        self.parameters = parameters


class UnbindResponse(AsyncResponse):
    def __init__(self, operation: str):
        self.operation = operation


class UpdateResponse(AsyncResponse):
    def __init__(
        self,
        operation: Optional[str],
        dashboard_url: Optional[str],
        metadata: Optional[ServiceInstanceMetadata] = None,
    ):
        self.operation = operation
        self.dashboard_url = dashboard_url
        self.metadata = metadata


class DeprovisionResponse(AsyncResponse):
    def __init__(self, operation: str):
        self.operation = operation


class LastOperationResponse:
    def __init__(
        self,
        state: OperationState,
        description: str,
        instance_usable: Optional[bool] = None,
        update_repeatable: Optional[bool] = None,
    ):
        self.state = state.value
        self.description = description
        self.instance_usable = instance_usable
        self.update_repeatable = update_repeatable
