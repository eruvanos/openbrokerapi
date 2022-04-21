from enum import Enum
from typing import List, Optional, Union

from openbrokerapi.catalog import (
    ServiceDashboardClient,
    ServiceMetadata,
    ServicePlan,
)
from openbrokerapi.settings import DISABLE_SPACE_ORG_GUID_CHECK


class ProvisionDetails:
    def __init__(
        self,
        service_id: str,
        plan_id: str,
        organization_guid: str = None,
        space_guid: str = None,
        parameters: dict = None,
        context: dict = None,
        **kwargs
    ):
        self.service_id = service_id
        self.plan_id = plan_id
        self.organization_guid = organization_guid
        self.space_guid = space_guid
        self.parameters = parameters
        self.context = context

        # Usage context information
        if isinstance(context, dict) and "organization_guid" in context:
            if (
                organization_guid is not None
                and context["organization_guid"] != organization_guid
            ):
                raise TypeError(
                    "organization_guid does not match with context.organization_guid"
                )
            self.organization_guid = context["organization_guid"]
        if isinstance(context, dict) and "space_guid" in context:
            if space_guid is not None and context["space_guid"] != space_guid:
                raise TypeError("space_guid does not match with context.space_guid")
            self.space_guid = context["space_guid"]

        if DISABLE_SPACE_ORG_GUID_CHECK:
            pass
        elif None in (self.organization_guid, self.space_guid):
            raise TypeError("Organization and space guid are required.")

        # HTTP contextual data
        self.authorization_username = None  #: username of HTTP Basic Auth
        self.originating_identity = (
            None  #: decoded X-Broker-Originating-Identity HTTP Header
        )


class ProvisionState(Enum):
    IS_ASYNC = "is_async"
    SUCCESSFUL_CREATED = "successfully created"
    IDENTICAL_ALREADY_EXISTS = "exists with identical config"


class ProvisionedServiceSpec:
    def __init__(
        self,
        state: ProvisionState = ProvisionState.SUCCESSFUL_CREATED,
        dashboard_url: str = None,
        operation: str = None,
    ):
        self.state = state
        self.dashboard_url = dashboard_url
        self.operation = operation

    @property
    def is_async(self):
        return self.state == ProvisionState.IS_ASYNC


class GetInstanceDetailsSpec:
    def __init__(
        self,
        service_id: str,
        plan_id: str,
        dashboard_url: Optional[str] = None,
        parameters: Optional[dict] = None,
    ):
        self.service_id = service_id
        self.plan_id = plan_id
        self.dashboard_url = dashboard_url
        self.parameters = parameters


class DeprovisionDetails:
    def __init__(self, service_id: str, plan_id: str):
        self.service_id = service_id
        self.plan_id = plan_id
        # HTTP contextual data
        self.authorization_username = None  #: username of HTTP Basic Auth
        self.originating_identity = (
            None  #: decoded X-Broker-Originating-Identity HTTP Header
        )


class DeprovisionServiceSpec:
    def __init__(self, is_async: bool, operation: str = None):
        self.is_async = is_async
        self.operation = operation


class PreviousValues:
    def __init__(
        self,
        plan_id: str = None,
        service_id: str = None,
        organization_id: str = None,
        space_id: str = None,
        **kwargs
    ):
        self.plan_id = plan_id
        self.service_id = service_id
        self.organization_id = organization_id
        self.space_id = space_id


class UpdateDetails:
    def __init__(
        self,
        service_id: str,
        plan_id: str = None,
        parameters: dict = None,
        previous_values: dict = None,
        context: dict = None,
        **kwargs
    ):
        self.service_id = service_id
        self.plan_id = plan_id
        self.parameters = parameters
        self.previous_values = (
            PreviousValues(**previous_values) if previous_values else None
        )
        self.context = context
        # HTTP contextual data
        self.authorization_username = None  #: username of HTTP Basic Auth
        self.originating_identity = (
            None  #: decoded X-Broker-Originating-Identity HTTP Header
        )


class UpdateServiceSpec:
    def __init__(
        self,
        is_async: bool,
        operation: Optional[str] = None,
        dashboard_url: Optional[str] = None,
    ):
        self.is_async = is_async
        self.operation = operation
        self.dashboard_url = dashboard_url


class BindResource:
    def __init__(self, app_guid: str = None, route: str = None, **kwargs):
        self.app_guid = app_guid
        self.route = route


class BindDetails:
    def __init__(
        self,
        service_id: str,
        plan_id: str,
        app_guid: str = None,
        bind_resource: dict = None,
        parameters: dict = None,
        context: dict = None,
        **kwargs
    ):
        self.app_guid = app_guid
        self.plan_id = plan_id
        self.service_id = service_id
        self.parameters = parameters
        self.bind_resource = BindResource(**bind_resource) if bind_resource else None
        self.context = context
        # HTTP contextual data
        self.authorization_username = None  #: username of HTTP Basic Auth
        self.originating_identity = (
            None  #: decoded X-Broker-Originating-Identity HTTP Header
        )


class SharedDevice:
    def __init__(self, volume_id: str, mount_config: dict = None):
        self.volume_id = volume_id
        self.mount_config = mount_config


class VolumeMount:
    def __init__(
        self,
        driver: str,
        container_dir: str,
        mode: str,
        device_type: str,
        device: SharedDevice,
    ):
        self.driver = driver
        self.container_dir = container_dir
        self.mode = mode
        self.device_type = device_type
        self.device = device


class BindState(Enum):
    IS_ASYNC = "is_async"
    SUCCESSFUL_BOUND = "successfully created"
    IDENTICAL_ALREADY_EXISTS = "exists with identical config"


class Binding:
    def __init__(
        self,
        state=BindState.SUCCESSFUL_BOUND,
        credentials: dict = None,
        syslog_drain_url: str = None,
        route_service_url: str = None,
        volume_mounts: List[VolumeMount] = None,
        operation: Optional[str] = None,
    ):
        self.state = state
        self.credentials = credentials
        self.syslog_drain_url = syslog_drain_url
        self.route_service_url = route_service_url
        self.volume_mounts = volume_mounts
        self.operation = operation


class GetBindingSpec:
    def __init__(
        self,
        credentials: dict = None,
        syslog_drain_url: str = None,
        route_service_url: str = None,
        volume_mounts: List[VolumeMount] = None,
        parameters: Optional[dict] = None,
        **kwargs
    ):
        self.credentials = credentials
        self.syslog_drain_url = syslog_drain_url
        self.route_service_url = route_service_url
        self.volume_mounts = volume_mounts
        self.parameters = parameters


class UnbindDetails:
    def __init__(self, service_id: str, plan_id: str):
        self.plan_id = plan_id
        self.service_id = service_id
        # HTTP contextual data
        self.authorization_username = None  #: username of HTTP Basic Auth
        self.originating_identity = (
            None  #: decoded X-Broker-Originating-Identity HTTP Header
        )


class UnbindSpec:
    def __init__(self, is_async: bool, operation: str = None):
        self.is_async = is_async
        self.operation = operation


class OperationState(Enum):
    IN_PROGRESS = "in progress"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class LastOperation:
    def __init__(self, state: OperationState, description: str = None):
        self.state = state
        self.description = description


class Service:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        bindable: bool,
        plans: List[ServicePlan],
        tags: List[str] = None,
        requires: List[str] = None,
        metadata: ServiceMetadata = None,
        dashboard_client: ServiceDashboardClient = None,
        plan_updateable: bool = False,
        instances_retrievable: bool = False,
        bindings_retrievable: bool = False,
        **kwargs
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
        self.instances_retrievable = instances_retrievable
        self.bindings_retrievable = bindings_retrievable

        self.__dict__.update(kwargs)


class ServiceBroker:
    """
    Provides a service. This covers catalog, provision, update, bind, unbind, deprovision and last operation.
    """

    def catalog(self) -> Union[Service, List[Service]]:
        """
        Returns the services information which is provided by this broker.

        :return: Service or list of services
        """
        raise NotImplementedError()

    def provision(
        self, instance_id: str, details: ProvisionDetails, async_allowed: bool, **kwargs
    ) -> ProvisionedServiceSpec:
        """
        Further readings `CF Broker API#Provisioning <https://docs.cloudfoundry.org/services/api.html#provisioning>`_

        :param instance_id: Instance id provided by the platform
        :param details: Details about the service to create
        :param async_allowed: Client allows async creation
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: ProvisionedServiceSpec
        :raises ErrInstanceAlreadyExists: If instance already exists
        :raises ErrAsyncRequired: If async is required but not supported
        """
        raise NotImplementedError()

    def update(
        self, instance_id: str, details: UpdateDetails, async_allowed: bool, **kwargs
    ) -> UpdateServiceSpec:
        """
        Further readings `CF Broker API#Update <https://docs.cloudfoundry.org/services/api.html#updating_service_instance>`_

        :param instance_id: Instance id provided by the platform
        :param details: Details about the service to update
        :param async_allowed: Client allows async creation
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: UpdateServiceSpec
        :raises ErrAsyncRequired: If async is required but not supported
        """
        raise NotImplementedError()

    def deprovision(
        self,
        instance_id: str,
        details: DeprovisionDetails,
        async_allowed: bool,
        **kwargs
    ) -> DeprovisionServiceSpec:
        """
        Further readings `CF Broker API#Deprovisioning <https://docs.cloudfoundry.org/services/api.html#deprovisioning>`_

        :param instance_id: Instance id provided by the platform
        :param details: Details about the service to delete
        :param async_allowed: Client allows async creation
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: DeprovisionServiceSpec
        :raises ErrInstanceDoesNotExist: If instance does not exists
        :raises ErrAsyncRequired: If async is required but not supported
        """
        raise NotImplementedError()

    def bind(
        self,
        instance_id: str,
        binding_id: str,
        details: BindDetails,
        async_allowed: bool,
        **kwargs
    ) -> Binding:
        """
        Further readings `CF Broker API#Binding <https://docs.cloudfoundry.org/services/api.html#binding>`_

        :param instance_id: Instance id provided by the platform
        :param binding_id: Binding id provided by the platform
        :param details: Details about the binding to create
        :param async_allowed: Client allows async binding
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: Binding
        :raises ErrBindingAlreadyExists: If binding already exists
        :raises ErrAppGuidNotProvided: If AppGuid is required but not provided
        """
        raise NotImplementedError()

    def unbind(
        self,
        instance_id: str,
        binding_id: str,
        details: UnbindDetails,
        async_allowed: bool,
        **kwargs
    ) -> UnbindSpec:
        """
        Further readings `CF Broker API#Unbinding <https://docs.cloudfoundry.org/services/api.html#unbinding>`_

        :param instance_id: Instance id provided by the platform
        :param binding_id: Binding id provided by the platform
        :param details: Details about the binding to delete
        :param async_allowed: Client allows async unbind
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: UnbindDetails
        :raises ErrBindingAlreadyExists: If binding already exists
        """
        raise NotImplementedError()

    def get_instance(self, instance_id: str, **kwargs) -> GetInstanceDetailsSpec:
        """
        Further readings `CF Broker API#FetchServiceInstance <https://github.com/openservicebrokerapi/servicebroker/blob/v2.14/spec.md#fetching-a-service-instance>`_
        Must be implemented if `"instances_retrievable" :true` is declared for a service in `catalog`.

        :param instance_id: Instance id provided by the platform
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: GetInstanceDetailsSpec
        :raises ErrInstanceDoesNotExist: If instance does not exists
        :raises ErrConcurrentInstanceAccess: If instance is being updated
        """
        raise NotImplementedError()

    def get_binding(
        self, instance_id: str, binding_id: str, **kwargs
    ) -> GetBindingSpec:
        """
        Further readings `CF Broker API#FetchServiceBinding <https://github.com/openservicebrokerapi/servicebroker/blob/v2.14/spec.md#fetching-a-service-binding>`_
        Must be implemented if `"bindings_retrievable" :true` is declared for a service in `catalog`.

        :param instance_id: Instance id provided by the platform
        :param binding_id: Instance id provided by the platform
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: GetBindingSpec
        :raises ErrBindingDoesNotExist: If binding does not exist
        """
        raise NotImplementedError()

    def last_operation(
        self,
        instance_id: str,
        operation_data: Optional[str],
        service_id: Optional[str],
        plan_id: Optional[str],
        **kwargs
    ) -> LastOperation:
        """
        Further readings `CF Broker API#LastOperation <https://docs.cloudfoundry.org/services/api.html#polling>`_

        :param instance_id: Instance id provided by the platform
        :param operation_data: Operation data received from async operation
        :param service_id: service identifier
        :param plan_id: plan identifier
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: LastOperation
        """
        raise NotImplementedError()

    def last_binding_operation(
        self,
        instance_id: str,
        binding_id: str,
        operation_data: Optional[str],
        service_id: Optional[str],
        plan_id: Optional[str],
        **kwargs
    ) -> LastOperation:
        """
        Further readings `CF Broker API#LastOperationForBindings <https://github.com/openservicebrokerapi/servicebroker/blob/v2.14/spec.md#polling-last-operation-for-service-bindings>`_
        Must be implemented if `Provision`, `Update`, or `Deprovision` are async.

        :param instance_id: Instance id provided by the platform
        :param binding_id: Binding id provided by the platform
        :param operation_data: Operation data received from async operation
        :param service_id: service identifier
        :param plan_id: plan identifier
        :param kwargs: May contain additional information, improves compatibility with upstream versions
        :rtype: LastOperation
        """
        raise NotImplementedError()
