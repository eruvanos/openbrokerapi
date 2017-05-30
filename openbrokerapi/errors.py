class ServiceExeption(BaseException):
    pass


class ErrInstanceAlreadyExists(ServiceExeption):
    def __init__(self):
        super().__init__("instance <already exists")


class ErrInstanceDoesNotExist(ServiceExeption):
    def __init__(self):
        super().__init__("instance does not exist")


class ErrInstanceLimitMet(ServiceExeption):
    def __init__(self):
        super().__init__("instance limit for this service has been reached")


class ErrPlanQuotaExceeded(ServiceExeption):
    def __init__(self):
        super().__init__("The quota for this service plan has been exceeded. Please contact your Operator for help.")


class ErrServiceQuotaExceeded(ServiceExeption):
    def __init__(self):
        super().__init__("The quota for this service has been exceeded. Please contact your Operator for help.")


class ErrBindingAlreadyExists(ServiceExeption):
    def __init__(self):
        super().__init__("binding already exists")


class ErrBindingDoesNotExist(ServiceExeption):
    def __init__(self):
        super().__init__("binding does not exist")


class ErrAsyncRequired(ServiceExeption):
    def __init__(self):
        super().__init__("This service plan requires client support for asynchronous service operations.")


class ErrPlanChangeNotSupported(ServiceExeption):
    def __init__(self):
        super().__init__("The requested plan migration cannot be performed")


class ErrAppGuidNotProvided(ServiceExeption):
    def __init__(self):
        super().__init__("app_guid is a required field but was not provided")
