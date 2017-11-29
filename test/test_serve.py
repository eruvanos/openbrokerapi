import time
from multiprocessing import Process
from typing import List
from unittest import TestCase

import requests

from openbrokerapi import api
from openbrokerapi import catalog
from openbrokerapi import service_broker


class ServeTest(TestCase):
    def test_serve_starts_server(self):
        def run_server():
            class TestBroker(service_broker.ServiceBroker):
                def catalog(self) -> List[catalog.Service]:
                    return []

            api.serve(TestBroker(), api.BrokerCredentials("", ""))

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
            class TestBroker(service_broker.ServiceBroker):
                def catalog(self) -> List[catalog.Service]:
                    return []

            api.serve(TestBroker(), None)

        server = Process(target=run_server)
        server.start()

        time.sleep(2)
        response = requests.get("http://localhost:5000/v2/catalog",
                                headers={'X-Broker-Api-Version': '2.13'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), dict(services=[]))

        server.terminate()
        server.join()
