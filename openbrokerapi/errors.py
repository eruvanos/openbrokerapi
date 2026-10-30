from typing import Optional


class ServiceException(Exception):
    """
    Base class of all broker errors.

    Optional keyword arguments (OSB API 2.17, "Service Broker Errors"):

    :param instance_usable: whether the service instance is still usable after a failed
        update or deprovision.
    :param update_repeatable: whether a failed update can be repeated.

    They are only added to the error body of update (PATCH) and deprovision (DELETE)
    requests (`update_repeatable` for update only); on every other endpoint they are ignored.
    Unset (`None`) means the field is omitted, which the spec defines as `true`.
    """

    def __init__(self, *args, instance_usable: Optional[bool] = None, update_repeatable: Optional[bool] = None):
        super().__init__(*args)
        self.instance_usable = instance_usable
        self.update_repeatable = update_repeatable


class ErrInstanceAlreadyExists(ServiceException):
    def __init__(self):
        super().__init__("Instance already exists")


class ErrInstanceDoesNotExist(ServiceException):
    def __init__(self):
        super().__init__("Instance does not exist")


class ErrInstanceNotFound(ServiceException):
    """
    Raise if the instance is unknown to the broker (HTTP 404).

    Use it in `last_operation` when the polled instance does not exist,
    e.g. while a provision is still in progress.
    Contrast with `ErrInstanceDoesNotExist` (HTTP 410), which means the instance
    is gone, e.g. an asynchronous deprovision has completed.
    """

    def __init__(self):
        super().__init__("Instance not found")


class ErrInstanceLimitMet(ServiceException):
    def __init__(self):
        super().__init__("Instance limit for this service has been reached")


class ErrPlanQuotaExceeded(ServiceException):
    def __init__(self):
        super().__init__("The quota for this service plan has been exceeded. Please contact your Operator for help.")


class ErrServiceQuotaExceeded(ServiceException):
    def __init__(self):
        super().__init__("The quota for this service has been exceeded. Please contact your Operator for help.")


class ErrBindingAlreadyExists(ServiceException):
    def __init__(self):
        super().__init__("Binding already exists")


class ErrBindingDoesNotExist(ServiceException):
    def __init__(self):
        super().__init__("Binding does not exist")


class ErrBindingNotFound(ServiceException):
    """
    Raise if the binding is unknown to the broker (HTTP 404).

    Use it in `last_binding_operation` when the polled binding does not exist,
    e.g. while a bind is still in progress.
    Contrast with `ErrBindingDoesNotExist` (HTTP 410), which means the binding
    is gone, e.g. an asynchronous unbind has completed.
    """

    def __init__(self):
        super().__init__("Binding not found")


class ErrInvalidParameters(ServiceException):
    def __init__(self, msg, **kwargs):
        super().__init__(msg, **kwargs)


class ErrAsyncRequired(ServiceException):
    def __init__(self, **kwargs):
        super().__init__("This service plan requires client support for asynchronous service operations.", **kwargs)


class ErrPlanChangeNotSupported(ErrInvalidParameters):
    def __init__(self, **kwargs):
        super().__init__("The requested plan migration cannot be performed", **kwargs)


class ErrAppGuidNotProvided(ServiceException):
    def __init__(self):
        super().__init__("app_guid is a required field but was not provided")


class ErrConcurrentInstanceAccess(ServiceException):
    def __init__(self, **kwargs):
        super().__init__("ConcurrencyError", **kwargs)


class ErrBadRequest(ServiceException):
    """
    Raise if malformed or missing mandatory data
    """

    def __init__(self, msg="Malformed or missing data", **kwargs):
        super().__init__(msg, **kwargs)


class ErrMaintenanceInfoConflict(ServiceException):
    """
    Raise if `maintenance_info.version` of the request does not match the
    version in the catalog (HTTP 422, error code "MaintenanceInfoConflict").
    """

    def __init__(self, msg="The maintenance information for the requested Service Plan has changed."):
        super().__init__(msg)
