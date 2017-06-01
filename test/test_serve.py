import time
import requests

from multiprocessing import Process
from typing import List
from unittest import TestCase

from openbrokerapi import api
from openbrokerapi import service_broker


class ServeTest(TestCase):
    def test_serve_starts_server(self):
        def run_server():
            class TestBroker(service_broker.ServiceBroker):
                def catalog(self) -> List[api.Service]:
                    return []

            api.serve(TestBroker(), api.BrokerCredentials("", ""))

        server = Process(target=run_server)
        server.start()

        time.sleep(2)
        response = requests.get("http://localhost:5000/v2/catalog",
                                auth=("", ""),
                                headers={'X-Broker-Api-Version': '2.10'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), dict(services=[]))

        server.terminate()
        server.join()
