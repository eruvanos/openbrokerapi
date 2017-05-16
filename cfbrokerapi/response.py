from typing import List

from cfbrokerapi.catalog import Service


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



