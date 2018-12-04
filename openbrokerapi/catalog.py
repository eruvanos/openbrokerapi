from typing import List, Dict, Optional


class ServiceMetadata:
    def __init__(self,
                 displayName: str,
                 imageUrl: str,
                 longDescription: str,
                 providerDisplayName: str,
                 documentationUrl: str,
                 supportUrl: str,
                 shareable: Optional[bool] = None
                 ):
        self.displayName = displayName
        self.imageUrl = imageUrl
        self.longDescription = longDescription
        self.providerDisplayName = providerDisplayName
        self.documentationUrl = documentationUrl
        self.supportUrl = supportUrl
        self.shareable = shareable


class ServiceDashboardClient:
    def __init__(self,
                 redirect_uri: str,
                 id: str = None,
                 secret: str = None
                 ):
        self.id = id
        self.secret = secret
        self.redirect_uri = redirect_uri


class ServicePlanCost:
    def __init__(self,
                 amount: Dict[str, int],
                 unit: str):
        self.amount = amount
        self.unit = unit


class ServicePlanMetaData:
    def __init__(self,
                 displayName: str = None,
                 bullets: List[str] = None,
                 costs: List[ServicePlanCost] = None
                 ):
        self.displayName = displayName
        self.bullets = bullets
        self.costs = costs


class Schemas:
    def __init__(self,
                 service_instance: Dict = None,
                 service_binding: Dict = None):
        self.service_instance = service_instance
        self.service_binding = service_binding


class ServicePlan:
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 metadata: ServicePlanMetaData = None,
                 free: bool = None,
                 bindable: bool = None,
                 schemas: Schemas = None
                 ):
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata
        self.free = free
        self.bindable = bindable
        self.schemas = schemas
