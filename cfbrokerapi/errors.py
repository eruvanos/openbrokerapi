class ErrInstanceAlreadyExists(BaseException):
    def __init__(self):
        super().__init__("instance already exists")


class ErrInstanceDoesNotExist(BaseException):
    def __init__(self):
        super().__init__("instance does not exist")


class ErrInstanceLimitMet(BaseException):
    def __init__(self):
        super().__init__("instance limit for this service has been reached")


class ErrPlanQuotaExceeded(BaseException):
    def __init__(self):
        super().__init__("The quota for this service plan has been exceeded. Please contact your Operator for help.")


class ErrServiceQuotaExceeded(BaseException):
    def __init__(self):
        super().__init__("The quota for this service has been exceeded. Please contact your Operator for help.")


class ErrBindingAlreadyExists(BaseException):
    def __init__(self):
        super().__init__("binding already exists")


class ErrBindingDoesNotExist(BaseException):
    def __init__(self):
        super().__init__("binding does not exist")


class ErrAsyncRequired(BaseException):
    def __init__(self):
        super().__init__("This service plan requires client support for asynchronous service operations.")


class ErrPlanChangeNotSupported(BaseException):
    def __init__(self):
        super().__init__("The requested plan migration cannot be performed")


class ErrRawParamsInvalid(BaseException):
    def __init__(self):
        super().__init__("The format of the parameters is not valid JSON")


class ErrAppGuidNotProvided(BaseException):
    def __init__(self):
        super().__init__("app_guid is a required field but was not provided")
