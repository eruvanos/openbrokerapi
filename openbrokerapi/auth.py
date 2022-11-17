from abc import abstractmethod
from http import HTTPStatus

from openbrokerapi.helper import to_json_response
from openbrokerapi.response import ErrorResponse


class Authenticator:
    """
    Before request filter, authenticating a request
    """

    def __call__(self, *args, **kwargs):
        return self.authenticate()

    @abstractmethod
    def authenticate(self):
        """
        Implement an `flask.typing.BeforeRequestCallable`
        """
        pass


class BrokerCredentials:
    """
    Credentials, which will be used to validate authenticate requests
    """

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class BasicAuthenticator(Authenticator):
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
                if (
                    auth.username == credential.username
                    and auth.password == credential.password
                ):
                    return
        return (
            to_json_response(
                ErrorResponse(
                    description="Could not verify your access level for that URL.\nYou have to login with proper credentials"
                )
            ),
            HTTPStatus.UNAUTHORIZED,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )


class NoneAuthenticator(Authenticator):
    """
    No authentication at all.
    """

    def authenticate(self):
        pass
