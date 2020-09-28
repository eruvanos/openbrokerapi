import logging
import functools
import inspect

from jsonschema import Draft4Validator, validators
from jsonschema import ValidationError
from openbrokerapi.catalog import ServicePlan
from openbrokerapi.errors import ErrInvalidParameters
from openbrokerapi.helper import ensure_list


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

prout = {
    "provision": ("service_instance", "create"),
    "update": ("service_instance", "update"),
    "bind": ("service_binding", "create")
}


def validate_parameters(validator_version=Draft4Validator):
    def decorate_validate_parameters(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            schema = {}
            fas = inspect.getfullargspec(func)
            details = args[fas.args.index("details")]
            self = args[0]
            try:
                step, op = prout[func.__name__]
                plan = _get_plan_id(self, details.plan_id)
                schema = plan.schemas.__getattribute__(step)[op]['parameters']
            except AttributeError as e:
                logging.error(e)
                pass
            try:
                validator = extend_with_default(validator_version)
                validator(schema).validate(details.parameters)
            except ValidationError as e:
                logging.error(e)
                raise ErrInvalidParameters(e)
            return func(*args, **kwargs)

        return wrapper

    return decorate_validate_parameters
