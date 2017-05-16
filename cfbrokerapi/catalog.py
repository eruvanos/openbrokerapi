from typing import List, Dict


class ServiceMetadata:
    def __init__(self):
        self.displayName: str
        self.imageUrl: str
        self.longDescription: str
        self.providerDisplayName: str
        self.documentationUrl: str
        self.supportUrl: str


class ServiceDashboardClient:
    def __init__(self):
        self.id: str
        self.secret: str
        self.redirect_uri: str


class ServicePlanCost:
    def __init__(self):
        self.amount: Dict[str, int]
        self.unit: str


class ServicePlanMetaData:
    def __init__(self):
        self.displayName: str
        self.bullets: List[str]
        self.costs: List[ServicePlanCost]


class ServicePlan:
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 metadata: ServicePlanMetaData = None,
                 free: bool = True,
                 bindable: bool = False
                 ):
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata
        self.free = free
        self.bindable = bindable


class Service:
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 bindable: bool,
                 plans: List[ServicePlan],
                 tags: List[str] = (),
                 requires: List[str]=(),
                 metadata: ServiceMetadata = None,
                 dashboard_client: ServiceDashboardClient = None,
                 plan_updateable: bool = False
                 ):
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
