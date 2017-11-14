from typing import List

from openbrokerapi.service_broker import OperationState, VolumeMount, Service


class EmptyResponse:
    pass


class ErrorResponse:
    def __init__(self,
                 error: str = None,
                 description: str = None):
        self.error = error
        self.description = description


class AsyncResponse:
    pass


class CatalogResponse:
    def __init__(self, services: List[Service]):
        self.services = services


class ProvisioningResponse(AsyncResponse):
    def __init__(self,
                 dashboard_url: str,
                 operation: str):
        self.dashboard_url = dashboard_url
        self.operation = operation


class BindResponse:
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


class UpdateResponse(AsyncResponse):
    def __init__(self, operation: str):
        self.operation = operation


class DeprovisionResponse(AsyncResponse):
    def __init__(self, operation: str):
        self.operation = operation


class LastOperationResponse:
    def __init__(self,
                 state: OperationState,
                 description: str
                 ):
        self.state = state.value
        self.description = description
