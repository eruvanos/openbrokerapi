import socket
import time

try:
    from gevent import monkey

    monkey.patch_all()
except ImportError:
    # fine if no gevent is available
    pass

import base64
import logging
from unittest.mock import Mock

from flask.app import Flask
from flask_testing import TestCase

from openbrokerapi.auth import BrokerCredentials
from openbrokerapi.log_util import basic_config


class BrokerTestCase(TestCase):
    auth_header = "Basic " + base64.b64encode(b":").decode("ascii")

    def create_app(self):
        from openbrokerapi.api import get_blueprint

        app = Flask(__name__)
        self.broker = Mock()

        app.register_blueprint(get_blueprint(self.broker, BrokerCredentials("", ""), basic_config(level=logging.WARN)))
        return app


def wait_for_port(port: int, host: str = "localhost", timeout: float = 5.0):
    """Wait until a port starts accepting TCP connections.
    Args:
        port: Port number.
        host: Host address on which the port should exist.
        timeout: In seconds. How long to wait before raising errors.
    Raises:
        TimeoutError: The port isn't accepting connection after time specified in `timeout`.
    """
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                break
        except OSError as ex:
            time.sleep(0.01)
            if time.perf_counter() - start_time >= timeout:
                raise TimeoutError(
                    f"Waited too long for the port {port} on host {host} to start accepting connections."
                ) from ex
