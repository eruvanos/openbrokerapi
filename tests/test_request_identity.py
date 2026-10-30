import http

from openbrokerapi import errors
from tests import BrokerTestCase

HEADER = "X-Broker-API-Request-Identity"


class RequestIdentityTest(BrokerTestCase):
    def setUp(self):
        self.broker.catalog.return_value = []

    def headers(self, **extra):
        h = {"X-Broker-Api-Version": "2.17", "Authorization": self.auth_header, HEADER: "req-123"}
        h.update(extra)
        return h

    def test_echoed_on_success(self):
        response = self.client.get("/v2/catalog", headers=self.headers())
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.headers[HEADER], "req-123")

    def test_not_added_when_not_sent(self):
        h = self.headers()
        del h[HEADER]
        response = self.client.get("/v2/catalog", headers=h)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertNotIn(HEADER, response.headers)

    def test_echoed_on_401(self):
        h = self.headers()
        del h["Authorization"]
        response = self.client.get("/v2/catalog", headers=h)
        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)
        self.assertEqual(response.headers[HEADER], "req-123")

    def test_echoed_on_412(self):
        response = self.client.get("/v2/catalog", headers=self.headers(**{"X-Broker-Api-Version": "2.9"}))
        self.assertEqual(response.status_code, http.HTTPStatus.PRECONDITION_FAILED)
        self.assertEqual(response.headers[HEADER], "req-123")

    def test_echoed_on_400_from_filter(self):
        response = self.client.put(
            "/v2/service_instances/abc",
            data="not json",
            headers=self.headers(),
        )
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.headers[HEADER], "req-123")

    def test_echoed_on_400_invalid_version(self):
        response = self.client.get("/v2/catalog", headers=self.headers(**{"X-Broker-Api-Version": "latest"}))
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.headers[HEADER], "req-123")

    def test_echoed_on_errorhandler_responses(self):
        for exc, status in [
            (errors.ErrInvalidParameters("x"), http.HTTPStatus.BAD_REQUEST),
            (NotImplementedError(), http.HTTPStatus.NOT_IMPLEMENTED),
            (RuntimeError("boom"), http.HTTPStatus.INTERNAL_SERVER_ERROR),
        ]:
            self.broker.catalog.side_effect = exc
            response = self.client.get("/v2/catalog", headers=self.headers())
            self.assertEqual(response.status_code, status)
            self.assertEqual(response.headers[HEADER], "req-123")


class InvalidVersionTest(BrokerTestCase):
    def setUp(self):
        self.broker.catalog.return_value = []

    def test_non_numeric_versions_return_400(self):
        for value in ["latest", "2.x", "2.", "..", "v2.13"]:
            response = self.client.get(
                "/v2/catalog", headers={"X-Broker-Api-Version": value, "Authorization": self.auth_header}
            )
            self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST, value)
            self.assertEqual(response.json, {"description": "Invalid X-Broker-API-Version header"})
