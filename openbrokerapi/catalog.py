from typing import List, Dict


class ServiceMetadata:
    def __init__(self,
                 displayName: str,
                 imageUrl: str,
                 longDescription: str,
                 providerDisplayName: str,
                 documentationUrl: str,
                 supportUrl: str):
        self.displayName = displayName
        self.imageUrl = imageUrl
        self.longDescription = longDescription
        self.providerDisplayName = providerDisplayName
        self.documentationUrl = documentationUrl
        self.supportUrl = supportUrl


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
                 service_instance=None,
                 service_binding=None):
        self.service_instance: Dict = service_instance
        self.service_binding: Dict = service_binding


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


class Service:
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 bindable: bool,
                 plans: List[ServicePlan],
                 tags: List[str] = None,
                 requires: List[str] = None,
                 metadata: ServiceMetadata = None,
                 dashboard_client: ServiceDashboardClient = None,
                 plan_updateable: bool = False
                 ):
        """
        :param requires:  syslog_drain, route_forwarding or volume_mount
        """
        self.id = id
        self.name = name
        self.description = description
        self.bindable = bindable
        self.plans = plans
        self.tags = tags
        self.requires = requires
        self.metadata = metadata
        self.dashboard_client = dashboard_client
        self.plan_updateable = plan_updateable
