import base64
import functools
import logging
from http import HTTPStatus

from openbrokerapi.helper import to_json_response, version_tuple
from openbrokerapi.response import ErrorResponse
from openbrokerapi.settings import MIN_VERSION

logger = logging.getLogger(__name__)


def print_request():
    from flask import request

    logger.debug("--- Request Start -------------------")
    logger.debug("--- Header")
    for k, v in request.headers:
        logger.debug("%s:%s", k, v)
    logger.debug("--- Body")
    logger.debug(request.data)
    logger.debug("--- Request End ---------------------")


def check_originating_identity():
    """
    Check and decode the "X-Broker-API-Originating-Identity" header
    https://github.com/openservicebrokerapi/servicebroker/blob/v2.13/spec.md#originating-identity
    """
    from flask import request, json

    if "X-Broker-API-Originating-Identity" in request.headers:
        try:
            platform, value = request.headers[
                "X-Broker-API-Originating-Identity"
            ].split(None, 1)
            request.originating_identity = {
                "platform": platform,
                "value": json.loads(base64.standard_b64decode(value)),
            }
        except ValueError as e:
            return (
                to_json_response(
                    ErrorResponse(
                        description='Improper "X-Broker-API-Originating-Identity" header. '
                        + str(e)
                    )
                ),
                HTTPStatus.BAD_REQUEST,
            )
    else:
        request.originating_identity = None


def requires_application_json(f):
    """Decorator for enforcing application/json Content-Type"""

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        from flask import request

        if request.get_json(silent=True) is None:
            er = ErrorResponse(
                description='Improper Content-Type header. Expecting "application/json"'
            )
            return to_json_response(er), HTTPStatus.BAD_REQUEST
        else:
            return f(*args, **kwargs)

    return wrapped


def get_auth_filter(broker_credentials):
    def requires_auth():
        """Check authentication over all provided usernames else sends a 401 response that enables basic auth"""
        from flask import request

        auth = request.authorization
        if auth:
            for credentials in broker_credentials:
                if (
                    auth.username == credentials.username
                    and auth.password == credentials.password
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

    return requires_auth


def check_version():
    from flask import request

    version = request.headers.get("X-Broker-Api-Version", None)
    if not version:
        return (
            to_json_response(
                ErrorResponse(description="No X-Broker-Api-Version found.")
            ),
            HTTPStatus.BAD_REQUEST,
        )
    if MIN_VERSION > version_tuple(version):
        return (
            to_json_response(
                ErrorResponse(
                    description="Service broker requires version %d.%d+." % MIN_VERSION
                )
            ),
            HTTPStatus.PRECONDITION_FAILED,
        )
