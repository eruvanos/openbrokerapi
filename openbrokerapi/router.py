from logging import getLogger
from typing import List, Optional, Set, Tuple, Type

from openbrokerapi import errors
from openbrokerapi.helper import ensure_list
from openbrokerapi.service_broker import (
    ServiceBroker,
    Service,
    ProvisionDetails,
    ProvisionedServiceSpec,
    UpdateDetails,
    UpdateServiceSpec,
    DeprovisionDetails,
    DeprovisionServiceSpec,
    BindDetails,
    Binding,
    BindState,
    UnbindDetails,
    UnbindSpec,
    LastOperation,
    GetInstanceDetailsSpec,
    GetBindingSpec,
)

logger = getLogger(__name__)


class Router(ServiceBroker):
    def __init__(self, *service_brokers: ServiceBroker):
        self._service_brokers = service_brokers

    @staticmethod
    def _service_ids(broker: ServiceBroker) -> Set[str]:
        return {service.id for service in ensure_list(broker.catalog())}

    def _get_provider_by_id(self, service_id: str) -> ServiceBroker:
        for broker in self._service_brokers:
            if service_id in self._service_ids(broker):
                return broker
        raise KeyError("Service {} not found".format(service_id))

    def _split_operation(self, operation_data: Optional[str]) -> Tuple[ServiceBroker, Optional[str]]:
        """
        Splits an operation string created by `add_service_id_to_async_response`
        into the provider and the provider's own operation data.
        """
        if operation_data is None:
            raise errors.ErrInvalidParameters("Invalid operation string")

        data = operation_data.split(" ", maxsplit=1)
        routed_service_id = data[0]
        provider_operation_data = data[1] if len(data) == 2 else None
        try:
            provider = self._get_provider_by_id(routed_service_id)
        except KeyError as e:
            logger.exception(e)
            raise errors.ErrInvalidParameters("Invalid operation string") from e

        return provider, provider_operation_data

    def _find_resource(self, method_name: str, not_found_error: Type[errors.ServiceException], *args, **kwargs):
        """
        Calls `method_name` on the provider of the `service_id` hint if given.
        Otherwise asks each provider in turn; providers raising `not_found_error`
        or `NotImplementedError` are treated as "not mine".
        """
        service_id = kwargs.get("service_id")
        if service_id is not None:
            try:
                provider = self._get_provider_by_id(service_id)
            except KeyError as e:
                logger.exception(e)
                raise not_found_error() from e
            return getattr(provider, method_name)(*args, **kwargs)

        any_implemented = False
        for provider in self._service_brokers:
            try:
                return getattr(provider, method_name)(*args, **kwargs)
            except not_found_error:
                any_implemented = True
            except NotImplementedError:
                pass

        if not any_implemented:
            raise NotImplementedError()
        raise not_found_error()

    @staticmethod
    def add_service_id_to_async_response(response, service_id: str):
        if response is None:
            return

        if isinstance(response, Binding):
            is_async = response.state == BindState.IS_ASYNC
        else:
            is_async = response.is_async

        if is_async:
            if response.operation is None:
                response.operation = service_id
            else:
                response.operation = " ".join((service_id, response.operation))

    def catalog(self) -> List[Service]:
        services = []
        for broker in self._service_brokers:
            services.extend(ensure_list(broker.catalog()))
        return services

    def provision(
        self, instance_id: str, details: ProvisionDetails, async_allowed: bool, **kwargs
    ) -> ProvisionedServiceSpec:
        provider = self._get_provider_by_id(details.service_id)

        result = provider.provision(instance_id, details, async_allowed, **kwargs)
        self.add_service_id_to_async_response(result, details.service_id)

        return result

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool, **kwargs) -> UpdateServiceSpec:
        provider = self._get_provider_by_id(details.service_id)
        result = provider.update(instance_id, details, async_allowed, **kwargs)
        self.add_service_id_to_async_response(result, details.service_id)

        return result

    def deprovision(
        self, instance_id: str, details: DeprovisionDetails, async_allowed: bool, **kwargs
    ) -> DeprovisionServiceSpec:
        provider = self._get_provider_by_id(details.service_id)
        result = provider.deprovision(instance_id, details, async_allowed, **kwargs)
        self.add_service_id_to_async_response(result, details.service_id)

        return result

    def bind(self, instance_id: str, binding_id: str, details: BindDetails, async_allowed: bool, **kwargs) -> Binding:
        provider = self._get_provider_by_id(details.service_id)
        result = provider.bind(instance_id, binding_id, details, async_allowed, **kwargs)
        self.add_service_id_to_async_response(result, details.service_id)

        return result

    def unbind(
        self, instance_id: str, binding_id: str, details: UnbindDetails, async_allowed: bool, **kwargs
    ) -> UnbindSpec:
        provider = self._get_provider_by_id(details.service_id)
        result = provider.unbind(instance_id, binding_id, details, async_allowed, **kwargs)
        self.add_service_id_to_async_response(result, details.service_id)

        return result

    def get_instance(self, instance_id: str, **kwargs) -> GetInstanceDetailsSpec:
        return self._find_resource("get_instance", errors.ErrInstanceDoesNotExist, instance_id, **kwargs)

    def get_binding(self, instance_id: str, binding_id: str, **kwargs) -> GetBindingSpec:
        return self._find_resource("get_binding", errors.ErrBindingDoesNotExist, instance_id, binding_id, **kwargs)

    def last_operation(
        self,
        instance_id: str,
        operation_data: Optional[str],
        service_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        **kwargs,
    ) -> LastOperation:
        provider, provider_operation_data = self._split_operation(operation_data)

        return provider.last_operation(
            instance_id, provider_operation_data, service_id=service_id, plan_id=plan_id, **kwargs
        )

    def last_binding_operation(
        self,
        instance_id: str,
        binding_id: str,
        operation_data: Optional[str],
        service_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        **kwargs,
    ) -> LastOperation:
        provider, provider_operation_data = self._split_operation(operation_data)

        return provider.last_binding_operation(
            instance_id, binding_id, provider_operation_data, service_id=service_id, plan_id=plan_id, **kwargs
        )
