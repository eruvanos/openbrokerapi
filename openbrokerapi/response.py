from typing import List

from openbrokerapi.catalog import Service
from openbrokerapi.service_broker import OperationState


class EmptyResponse:
    pass


class ErrorResponse:
    def __init__(self,
                 error: str = None,
                 description: str = None):
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
                 state: OperationState,
                 description: str
                 ):
        self.state = state.value
        self.description = description
