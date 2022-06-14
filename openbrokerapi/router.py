from logging import getLogger
from typing import List, Optional, Set

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
    UnbindDetails,
    LastOperation,
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

    @staticmethod
    def add_service_id_to_async_response(response, service_id: str):
        if response.is_async:
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

    def update(
        self, instance_id: str, details: UpdateDetails, async_allowed: bool, **kwargs
    ) -> UpdateServiceSpec:
        provider = self._get_provider_by_id(details.service_id)
        result = provider.update(instance_id, details, async_allowed, **kwargs)
        self.add_service_id_to_async_response(result, details.service_id)

        return result

    def deprovision(
        self,
        instance_id: str,
        details: DeprovisionDetails,
        async_allowed: bool,
        **kwargs
    ) -> DeprovisionServiceSpec:
        provider = self._get_provider_by_id(details.service_id)
        result = provider.deprovision(instance_id, details, async_allowed, **kwargs)
        self.add_service_id_to_async_response(result, details.service_id)

        return result

    def bind(
        self,
        instance_id: str,
        binding_id: str,
        details: BindDetails,
        async_allowed: bool,
        **kwargs
    ) -> Binding:
        provider = self._get_provider_by_id(details.service_id)
        result = provider.bind(instance_id, binding_id, details, False, **kwargs)

        return result

    def unbind(
        self,
        instance_id: str,
        binding_id: str,
        details: UnbindDetails,
        async_allowed: bool,
        **kwargs
    ):
        provider = self._get_provider_by_id(details.service_id)
        result = provider.unbind(instance_id, binding_id, details, False, **kwargs)

        return result

    def last_operation(
        self, instance_id: str, operation_data: Optional[str], **kwargs
    ) -> LastOperation:
        if operation_data is None:
            raise errors.ErrInvalidParameters("Invalid operation string")

        data = operation_data.split(" ", maxsplit=1)
        service_id = data[0]
        operation_data = data[1] if len(data) == 2 else None
        try:
            provider = self._get_provider_by_id(service_id)
        except KeyError as e:
            logger.exception(e)
            raise errors.ErrInvalidParameters("Invalid operation string")

        return provider.last_operation(instance_id, operation_data, **kwargs)
