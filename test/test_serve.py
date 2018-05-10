import time
from multiprocessing import Process
from unittest import TestCase
from unittest.mock import Mock

import requests

from openbrokerapi import api
from openbrokerapi.service_broker import Service


class ServeTest(TestCase):
    def test_serve_starts_server(self):
        def run_server():
            api.serve([], api.BrokerCredentials("", ""))

        server = Process(target=run_server)
        server.start()

        time.sleep(2)
        response = requests.get("http://localhost:5000/v2/catalog",
                                auth=("", ""),
                                headers={'X-Broker-Api-Version': '2.13'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), dict(services=[]))

        server.terminate()
        server.join()

    def test_serve_starts_server_without_auth(self):
        def run_server():
            api.serve([], None)

        server = Process(target=run_server)
        server.start()

        time.sleep(2)
        response = requests.get("http://localhost:5000/v2/catalog",
                                headers={'X-Broker-Api-Version': '2.13'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), dict(services=[]))

        server.terminate()
        server.join()

    def test_serve_starts_with_single_instance(self):
        def run_server():
            broker = Mock()
            broker.catalog.return_value = Service('id', 'name', 'description', False, [])
            api.serve(broker, [api.BrokerCredentials("cfy-login", "cfy-pwd"),
                               api.BrokerCredentials("k8s-login", "k8s-pwd")])

        server = Process(target=run_server)
        server.start()

        time.sleep(2)
        response = requests.get("http://localhost:5000/v2/catalog",
                                auth=("k8s-login", "k8s-pwd"),
                                headers={'X-Broker-Api-Version': '2.13'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), dict(services=[{'bindable': False,
                                                          'description': 'description',
                                                          'id': 'id',
                                                          'name': 'name',
                                                          'plan_updateable': False,
                                                          'plans': []}]))
        server.terminate()
        server.join()
