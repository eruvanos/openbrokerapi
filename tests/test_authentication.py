import logging
from unittest import TestCase
from uuid import uuid4

from flask import Flask
from flask.testing import FlaskClient

from openbrokerapi.api import get_blueprint
from openbrokerapi.auth import Authenticator
from tests.test_serve import InMemBroker


class _CustomAuthenticator(Authenticator):
    last_token = None

    def authenticate(self):
        from flask import request

        self.last_token = request.headers["Authorization"]

        return "Hit test", 401


class AuthenticationTest(TestCase):
    def test_custom_authentication(self):
        app = Flask(__name__)

        authenticator = _CustomAuthenticator()
        auth_token = str(uuid4())

        app.register_blueprint(
            get_blueprint(
                service_broker=InMemBroker(),
                broker_credentials=None,
                logger=logging.getLogger(__name__),
                authenticator=authenticator,
            )
        )

        with app.test_client() as client:
            client: FlaskClient
            res = client.get(
                "/v2/catalog",
                headers={"X-Broker-Api-Version": "2.13", "Authorization": auth_token},
            )
            self.assertEqual(401, res.status_code)

        self.assertEqual(auth_token, authenticator.last_token)
