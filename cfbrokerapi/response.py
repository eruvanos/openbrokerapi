from typing import List

from cfbrokerapi.catalog import Service


class EmptyResponse(dict):
    pass


class ErrorResponse:
    def __init__(self,
                 error: str,
                 description: str):
        self.error = error
        self.description = description


class CatalogResponse:
    def __init__(self, services: List[Service]):
        self.services = services


class ProvisioningResponse:
    def __init__(self,
                 dashboard_url: str,
                 operation: str):
        self.dashboard_url = dashboard_url
        self.operation = operation


class UpdateResponse:
    def __init__(self, operation: str):
        self.operation = operation


class DeprovisionResponse:
    def __init__(self, operation: str):
        self.operation = operation


class LastOperationResponse:
    def __init__(self,
                 state: dict,  # LastOperationState,
                 description: str
                 ):
        self.state = state
        self.description = description


class ExperimentalVolumeMountPrivate:
    def __init__(self,
                 driver: str,
                 group_id: str,
                 config: str
                 ):
        self.driver = driver
        self.group_id = group_id
        self.config = config


class ExperimentalVolumeMount:
    def __init__(self,
                 container_path: str,
                 mode: str,
                 private: ExperimentalVolumeMountPrivate
                 ):
        self.container_path = container_path
        self.mode = mode
        self.private = private


class ExperimentalVolumeMountBindingResponse:
    def __init__(self,
                 credentials: dict,
                 syslog_drain_url: str,
                 route_service_url: str,
                 volume_mounts: List[ExperimentalVolumeMount]
                 ):
        self.credentials = credentials
        self.syslog_drain_url = syslog_drain_url
        self.route_service_url = route_service_url
        self.volume_mounts = volume_mounts
