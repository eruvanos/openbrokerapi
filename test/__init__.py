import base64
from unittest.mock import Mock

import logging
from flask.app import Flask
from flask_testing import TestCase

from openbrokerapi.log_util import basic_config
from openbrokerapi.api import BrokerCredentials
from openbrokerapi.service_broker import ServiceBroker


class BrokerTestCase(TestCase):
    auth_header = 'Basic ' + base64.b64encode(b":").decode("ascii")

    def create_app(self):
        from openbrokerapi.api import get_blueprint

        app = Flask(__name__)
        self.broker: ServiceBroker = Mock()

        app.register_blueprint(
            get_blueprint(self.broker,
                          BrokerCredentials("", ""),
                          basic_config(level=logging.NOTSET)
                          )
        )
        return app
