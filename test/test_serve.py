import time
from multiprocessing import Process
from unittest import TestCase

import requests

from openbrokerapi import api


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
