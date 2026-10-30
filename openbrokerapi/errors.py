class ServiceException(Exception):
    pass


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
    def __init__(self, msg):
        super().__init__(msg)


class ErrAsyncRequired(ServiceException):
    def __init__(self):
        super().__init__("This service plan requires client support for asynchronous service operations.")


class ErrPlanChangeNotSupported(ErrInvalidParameters):
    def __init__(self):
        super().__init__("The requested plan migration cannot be performed")


class ErrAppGuidNotProvided(ServiceException):
    def __init__(self):
        super().__init__("app_guid is a required field but was not provided")


class ErrConcurrentInstanceAccess(ServiceException):
    def __init__(self):
        super().__init__("ConcurrencyError")


class ErrBadRequest(ServiceException):
    """
    Raise if malformed or missing mandatory data
    """

    def __init__(self, msg="Malformed or missing data"):
        super().__init__(msg)


class ErrMaintenanceInfoConflict(ServiceException):
    """
    Raise if `maintenance_info.version` of the request does not match the
    version in the catalog (HTTP 422, error code "MaintenanceInfoConflict").
    """

    def __init__(self, msg="The maintenance information for the requested Service Plan has changed."):
        super().__init__(msg)
