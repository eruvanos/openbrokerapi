import logging
from typing import Optional, Union, List

from openbrokerapi.api import ServiceBroker
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.errors import ErrInvalidParameters
from openbrokerapi.helper import ensure_list
from openbrokerapi.service_broker import LastOperation, GetBindingSpec, GetInstanceDetailsSpec, UnbindDetails, \
    UnbindSpec, BindDetails, Binding, UpdateDetails, UpdateServiceSpec, Service, ProvisionDetails, \
    ProvisionedServiceSpec, DeprovisionDetails, DeprovisionServiceSpec

from jsonschema import Draft4Validator, validators
from jsonschema import ValidationError


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": set_defaults},
    )


class SchemaValidator(ServiceBroker):
    """
    Validate parameters against schema
    """
    def __init__(self, sb, draft=Draft4Validator):
        self.sb = sb
        self.json_schema_draft = draft

    def _get_plan_id(self, plan_id) -> ServicePlan:
        """
        Return the service plan for the plan_id in the catalog
        :return: ServicePlan
        """
        for service in ensure_list(self.catalog()):
            for plan in service.plans:
                if plan.id == plan_id:
                    return plan
        return False

    def _validate_schema(self, details, step, op):
        schema = {}
        try:
            plan = self._get_plan_id(details.plan_id)
            schema = plan.schemas.__getattribute__(step)[op]['parameters']
        except AttributeError:
            pass
        try:
            Validator = extend_with_default(self.json_schema_draft)
            Validator(schema).validate(details.parameters)
        except ValidationError as e:
            logging.error(e)
            raise ErrInvalidParameters(e)

    def catalog(self) -> Union[Service, List[Service]]:
        return self.sb.catalog()

    def update(self, instance_id: str, details: UpdateDetails, async_allowed: bool, **kwargs) -> UpdateServiceSpec:
        self._validate_schema(details, 'service_instance', 'update')

        return self.sb.update(instance_id, details, async_allowed, **kwargs)

    def bind(self, instance_id: str, binding_id: str, details: BindDetails, async_allowed: bool, **kwargs) -> Binding:
        self._validate_schema(details, 'service_binding', 'create')

        return self.sb.bind(instance_id, binding_id, details, async_allowed, **kwargs)

    def unbind(self, instance_id: str, binding_id: str, details: UnbindDetails, async_allowed: bool,
               **kwargs) -> UnbindSpec:
        return self.sb.unbind(instance_id, binding_id, details, async_allowed, **kwargs)

    def get_instance(self, instance_id: str, **kwargs) -> GetInstanceDetailsSpec:
        return self.sb.get_instance(instance_id, **kwargs)

    def get_binding(self, instance_id: str, binding_id: str, **kwargs) -> GetBindingSpec:
        return self.sb.get_binding(instance_id, binding_id, **kwargs)

    def last_operation(self, instance_id: str, operation_data: Optional[str], **kwargs) -> LastOperation:
        return self.sb.last_operation(instance_id, operation_data, **kwargs)

    def last_binding_operation(self, instance_id: str, binding_id: str, operation_data: Optional[str],
                               **kwargs) -> LastOperation:
        return self.sb.last_operation(instance_id, operation_data, **kwargs)

    def provision(self,
                  instance_id: str,
                  details: ProvisionDetails,
                  async_allowed: bool,
                  **kwargs
                  ) -> ProvisionedServiceSpec:
        self._validate_schema(details,'service_instance', 'create')
        r = self.sb.provision(instance_id, details, async_allowed, **kwargs)
        return r

    def deprovision(self,
                    instance_id: str,
                    details: DeprovisionDetails,
                    async_allowed: bool,
                    **kwargs
                    ) -> DeprovisionServiceSpec:
        return self.sb.deprovision(instance_id, details, async_allowed, **kwargs)
