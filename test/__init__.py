import base64
import logging
from unittest.mock import Mock

from flask.app import Flask
from flask_testing import TestCase

from openbrokerapi.api import BrokerCredentials
from openbrokerapi.log_util import basic_config


class BrokerTestCase(TestCase):
    auth_header = 'Basic ' + base64.b64encode(b":").decode("ascii")

    def create_app(self):
        from openbrokerapi.api import get_blueprint

        app = Flask(__name__)
        self.broker = Mock()

        app.register_blueprint(
            get_blueprint(self.broker,
                          BrokerCredentials("", ""),
                          basic_config(level=logging.WARN)
                          )
        )
        return app
