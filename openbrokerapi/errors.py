class ServiceException(Exception):
    pass


class ErrInstanceAlreadyExists(ServiceException):
    def __init__(self):
        super().__init__("Instance already exists")


class ErrInstanceDoesNotExist(ServiceException):
    def __init__(self):
        super().__init__("Instance does not exist")


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


class ErrAsyncRequired(ServiceException):
    def __init__(self):
        super().__init__("This service plan requires client support for asynchronous service operations.")


class ErrPlanChangeNotSupported(ServiceException):
    def __init__(self):
        super().__init__("The requested plan migration cannot be performed")


class ErrAppGuidNotProvided(ServiceException):
    def __init__(self):
        super().__init__("app_guid is a required field but was not provided")
