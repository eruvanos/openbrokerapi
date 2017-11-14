import http

from openbrokerapi.service_broker import Service

from openbrokerapi.catalog import (
    ServiceDashboardClient,
    ServiceMetadata,
    ServicePlan,
    ServicePlanCost,
    ServicePlanMetaData,
)
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
        self.service.get_catalog.return_value = self.service_list[0]

        self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assertTrue(self.service.get_catalog.called)

    def test_catalog_ignores_request_headers(self):
        self.service.get_catalog.return_value = self.service_list[0]

        self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                "unknown": "unknown"
            })

        self.assertTrue(self.service.get_catalog.called)

    def test_catalog_returns_200_with_service_information(self):
        self.service.get_catalog.return_value = Service(
            id="s1",
            name="service_name",
            description="service_description",
            bindable=True,
            plans=[ServicePlan(
                id="p1",
                name="default",
                description="plan_description",
                metadata=ServicePlanMetaData(
                    displayName="displayName",
                    bullets=["bullet1"],
                    costs=[ServicePlanCost(
                        amount={"requests": 1},
                        unit="unit"
                    )]
                ),
                free=True,
                bindable=True
            )],
            tags=['tag1', 'tag2'],
            requires=['something'],
            metadata=ServiceMetadata(
                displayName="displayName",
                imageUrl="imageUrl",
                longDescription="longDescription",
                providerDisplayName="providerDisplayName",
                documentationUrl="documentationUrl",
                supportUrl="supportUrl"
            ),
            dashboard_client=ServiceDashboardClient(
                id="id",
                secret="secret",
                redirect_uri="redirect_uri"
            ),
            plan_updateable=True
        )

        response = self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                "unknown": "unknown"
            })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json,
                         dict(
                             services=[
                                 dict(id="s1",
                                      name="service_name",
                                      description="service_description",
                                      bindable=True,
                                      plans=[dict(
                                          id="p1",
                                          name="default",
                                          description="plan_description",
                                          metadata=dict(
                                              displayName="displayName",
                                              bullets=["bullet1"],
                                              costs=[dict(
                                                  amount={"requests": 1},
                                                  unit="unit"
                                              )]
                                          ),
                                          free=True,
                                          bindable=True
                                      )],
                                      tags=['tag1', 'tag2'],
                                      requires=['something'],
                                      metadata=dict(
                                          displayName="displayName",
                                          imageUrl="imageUrl",
                                          longDescription="longDescription",
                                          providerDisplayName="providerDisplayName",
                                          documentationUrl="documentationUrl",
                                          supportUrl="supportUrl"
                                      ),
                                      dashboard_client=dict(
                                          id="id",
                                          secret="secret",
                                          redirect_uri="redirect_uri"
                                      ),
                                      plan_updateable=True
                                      )
                             ]
                         ))

    def test_catalog_returns_200_with_minimal_service_information(self):
        self.service.get_catalog.return_value = self.service_list[0]

        response = self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                "unknown": "unknown"
            })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json,
                         dict(
                             services=[
                                 dict(
                                     id="s1",
                                     name="service_name",
                                     description="service_description",
                                     bindable=True,
                                     plan_updateable=False,
                                     plans=[dict(id="p1", name="default", description="plan_description")]
                                 )
                             ]
                         ))

    def test_catalog_returns_500_if_error_raised(self):
        self.service.get_catalog.side_effect = Exception("ERROR")

        response = self.client.get(
            "/v2/catalog",
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                "unknown": "unknown"
            })

        self.assertEqual(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json,
                         dict(
                             description="ERROR"
                         ))
