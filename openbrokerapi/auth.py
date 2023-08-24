from abc import abstractmethod
from typing import Union, Optional, Awaitable

from flask.typing import ResponseReturnValue

from openbrokerapi.helper import to_json_response
from openbrokerapi.response import ErrorResponse


class BrokerAuthenticator:
    """
    Before request filter, authenticating a request
    """

    def __call__(self, *args, **kwargs):
        return self.authenticate()

    @abstractmethod
    def authenticate(self) -> Union[
        Optional[ResponseReturnValue],
        Awaitable[Optional[ResponseReturnValue]]
    ]:
        """
        Implement an `flask.typing.BeforeRequestCallable`

        The function will be called without any arguments. If it returns a non-None value, the value is handled as
        if it was the return value from the broker, and further request handling is stopped.

        To deny access return something like

        .. code-block:: python

            (
                to_json_response(
                    ErrorResponse(
                        description="Could not verify your access level for that URL.\nYou have to login with proper credentials"
                    )
                ),
                401
            )
        """
        pass


class BrokerCredentials:
    """
    Credentials, which will be used to validate authenticate requests
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class BasicBrokerAuthenticator(BrokerAuthenticator):
    """
    Basic Authentication for openbrokerapi
    """

    def __init__(self, *credentials: BrokerCredentials):
        self._credentials = credentials

    def authenticate(self):
        """Check authentication over all provided usernames else sends a 401 response that enables basic auth"""
        from flask import request

        auth = request.authorization
        if auth:
            for credential in self._credentials:
                if auth.username == credential.username and auth.password == credential.password:
                    return
        return (
            to_json_response(
                ErrorResponse(
                    description="Could not verify your access level for that URL.\nYou have to login with proper credentials"
                )
            ),
            401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )


class NoneBrokerAuthenticator(BrokerAuthenticator):
    """
    No authentication at all.
    """

    def authenticate(self):
        pass


# Backwards compatible
Authenticator = BrokerAuthenticator
BasicAuthenticator = BasicBrokerAuthenticator
NoneAuthenticator = NoneBrokerAuthenticator
