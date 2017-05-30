import http

from openbrokerapi.catalog import *
from test import BrokerTestCase


class CatalogTest(BrokerTestCase):
    service_list = [
        Service(id="s1",
                name="service_name",
                description="service_description",
                bindable=True,
                plans=[ServicePlan(id="p1", name="default", description="plan_description")]
                )
    ]

    def test_catalog_called_with_the_right_values(self):
        self.broker.catalog.return_value = self.service_list

        _ = self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.broker.catalog.assert_called_once()

    def test_catalog_ignores_request_headers(self):
        self.broker.catalog.return_value = self.service_list

        _ = self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header,
                "unknown": "unknown"
            })

        self.broker.catalog.assert_called_once()

    def test_catalog_returns_200_with_service_list(self):
        self.broker.catalog.return_value = self.service_list

        response = self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header,
                "unknown": "unknown"
            })

        self.assertEquals(response.status_code, http.HTTPStatus.OK)
        self.assertEquals(response.json,
                          dict(
                              services=[
                                  dict(
                                      id="s1",
                                      name="service_name",
                                      description="service_description",
                                      bindable=True,
                                      plans=[dict(id="p1", name="default", description="plan_description")]
                                  )
                              ]
                          ))

    def test_catalog_returns_500_if_error_raised(self):
        self.broker.catalog.side_effect = Exception("ERROR")

        response = self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header,
                "unknown": "unknown"
            })

        self.assertEquals(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEquals(response.json,
                          dict(
                              description="ERROR"
                          ))