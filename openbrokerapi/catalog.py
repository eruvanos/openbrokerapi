from __future__ import annotations

from typing import List, Dict, Optional, Union


class ServiceMetadata:
    def __init__(
        self,
        displayName: str | None = None,
        imageUrl: str | None = None,
        longDescription: str | None = None,
        providerDisplayName: str | None = None,
        documentationUrl: str | None = None,
        supportUrl: str | None = None,
        shareable: Optional[bool] = None,
        **kwargs,
    ):
        self.displayName = displayName
        self.imageUrl = imageUrl
        self.longDescription = longDescription
        self.providerDisplayName = providerDisplayName
        self.documentationUrl = documentationUrl
        self.supportUrl = supportUrl
        self.shareable = shareable

        self.__dict__.update(kwargs)


class ServiceDashboardClient:
    def __init__(self, *, id: str, secret: Optional[str] = None, redirect_uri: Optional[str] = None, **kwargs):
        self.id = id
        self.secret = secret
        self.redirect_uri = redirect_uri

        self.__dict__.update(kwargs)


class ServicePlanCost:
    def __init__(self, amount: Dict[str, float], unit: str, **kwargs):
        self.amount = amount
        self.unit = unit

        self.__dict__.update(kwargs)


class ServicePlanMetadata:
    def __init__(
        self,
        displayName: Optional[str] = None,
        bullets: Optional[List[str]] = None,
        costs: Optional[List[ServicePlanCost]] = None,
        **kwargs,
    ):
        self.displayName = displayName
        self.bullets = bullets
        self.costs = costs

        self.__dict__.update(kwargs)


class Schemas:
    def __init__(self, service_instance: Optional[Dict] = None, service_binding: Optional[Dict] = None, **kwargs):
        self.service_instance = service_instance
        self.service_binding = service_binding

        self.__dict__.update(kwargs)


class MaintenanceInfo:
    def __init__(self, version: str, description: Optional[str] = None, **kwargs):
        self.version = version
        self.description = description

        self.__dict__.update(kwargs)


class ServicePlan:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        metadata: Optional[ServicePlanMetadata] = None,
        free: Optional[bool] = None,
        bindable: Optional[bool] = None,
        schemas: Optional[Schemas] = None,
        plan_updateable: Optional[bool] = None,
        maximum_polling_duration: Optional[int] = None,
        maintenance_info: Optional[Union[MaintenanceInfo, Dict]] = None,
        **kwargs,
    ):
        """
        Optional fields default to None and are omitted from the catalog when unset.

        :param plan_updateable: Overrides the service's ``plan_updateable`` for this plan
        :param maximum_polling_duration: Seconds the platform SHOULD use as maximum polling duration (OSB 2.15+)
        :param maintenance_info: ``MaintenanceInfo`` or dict with at least ``version``
        """
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata
        self.free = free
        self.bindable = bindable
        self.schemas = schemas
        self.plan_updateable = plan_updateable
        self.maximum_polling_duration = maximum_polling_duration
        self.maintenance_info = maintenance_info

        self.__dict__.update(kwargs)
