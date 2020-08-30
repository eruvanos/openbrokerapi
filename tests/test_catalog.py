import base64
import http

from openbrokerapi import constants
from openbrokerapi.catalog import (
    ServiceDashboardClient,
    ServiceMetadata,
    ServicePlan,
    ServicePlanCost,
    ServicePlanMetadata)
from openbrokerapi.service_broker import Service
from tests import BrokerTestCase


class CatalogTest(BrokerTestCase):
    service = Service(
        id='s1',
        name='service_name',
        description='service_description',
        bindable=True,
        plans=[ServicePlan(id='p1', name='default', description='plan_description')]
    )

    def test_catalog_called_with_the_right_values(self):
        self.broker.catalog.return_value = self.service

        self.client.get(
            '/v2/catalog',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.assertTrue(self.broker.catalog.called)

    def test_catalog_ignores_request_headers(self):
        self.broker.catalog.return_value = self.service

        self.client.get(
            '/v2/catalog',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                'unknown': 'unknown'
            })

        self.assertTrue(self.broker.catalog.called)

    def test_catalog_returns_200_with_service_information(self):
        '''
        This tests all the possible information a catalog could have. Including custom Service-/ServicePlanMetadata
        '''
        self.broker.catalog.return_value = Service(
            id='s1',
            name='service_name',
            description='service_description',
            bindable=True,
            plans=[ServicePlan(
                id='p1',
                name='default',
                description='plan_description',
                metadata=ServicePlanMetadata(
                    displayName='displayName',
                    bullets=['bullet1'],
                    costs=[ServicePlanCost(
                        amount={'requests': 1},
                        unit='unit'
                    )],
                    custom_field2='custom_field2'
                ),
                free=True,
                bindable=True
            )],
            tags=['tag1', 'tag2'],
            requires=['something'],
            metadata=ServiceMetadata(
                displayName='displayName',
                imageUrl='imageUrl',
                longDescription='longDescription',
                providerDisplayName='providerDisplayName',
                documentationUrl='documentationUrl',
                supportUrl='supportUrl',
                shareable=True,
                custom_field1='custom_field1'
            ),
            dashboard_client=ServiceDashboardClient(
                id='id',
                secret='secret',
                redirect_uri='redirect_uri'
            ),
            plan_updateable=True
        )

        response = self.client.get(
            '/v2/catalog',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                'unknown': 'unknown'
            })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json,
                         dict(
                             services=[
                                 dict(id='s1',
                                      name='service_name',
                                      description='service_description',
                                      instances_retrievable=False,
                                      bindings_retrievable=False,
                                      bindable=True,
                                      plans=[dict(
                                          id='p1',
                                          name='default',
                                          description='plan_description',
                                          metadata=dict(
                                              displayName='displayName',
                                              bullets=['bullet1'],
                                              costs=[dict(
                                                  amount={'requests': 1},
                                                  unit='unit'
                                              )],
                                              custom_field2='custom_field2'
                                          ),
                                          free=True,
                                          bindable=True
                                      )],
                                      tags=['tag1', 'tag2'],
                                      requires=['something'],
                                      metadata=dict(
                                          displayName='displayName',
                                          imageUrl='imageUrl',
                                          longDescription='longDescription',
                                          providerDisplayName='providerDisplayName',
                                          documentationUrl='documentationUrl',
                                          supportUrl='supportUrl',
                                          shareable=True,
                                          custom_field1='custom_field1'
                                      ),
                                      dashboard_client=dict(
                                          id='id',
                                          secret='secret',
                                          redirect_uri='redirect_uri'
                                      ),
                                      plan_updateable=True
                                      )
                             ]
                         ))

    def test_catalog_returns_200_with_minimal_service_information(self):
        self.broker.catalog.return_value = self.service

        response = self.client.get(
            '/v2/catalog',
            headers={
                'X-Broker-Api-Version': '2.13',
                'X-Broker-Api-Originating-Identity': 'test ' + base64.standard_b64encode(b'{"user_id":123}').decode(
                    'ascii'),
                'Authorization': self.auth_header,
                'unknown': 'unknown'
            })

        self.assertEqual(http.HTTPStatus.OK, response.status_code)
        self.assertEqual(response.json,
                         dict(
                             services=[
                                 dict(
                                     id='s1',
                                     name='service_name',
                                     description='service_description',
                                     instances_retrievable=False,
                                     bindings_retrievable=False,
                                     bindable=True,
                                     plan_updateable=False,
                                     plans=[dict(id='p1', name='default', description='plan_description')]
                                 )
                             ]
                         ))

    def test_catalog_returns_500_if_error_raised(self):
        self.broker.catalog.side_effect = Exception('ERROR')

        response = self.client.get(
            '/v2/catalog',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                'unknown': 'unknown'
            })

        self.assertEqual(response.status_code, http.HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json,
                         dict(
                             description=constants.DEFAULT_EXCEPTION_ERROR_MESSAGE
                         ))

    def test_catalog_can_return_multiple_services(self):
        self.broker.catalog.return_value = [
            Service(
                id='s1',
                name='service_name1',
                description='service_description1',
                bindable=True,
                plans=[ServicePlan(id='p1', name='default1', description='plan_description1')]
            ),
            Service(
                id='s2',
                name='service_name2',
                description='service_description2',
                bindable=True,
                plans=[ServicePlan(id='p2', name='default2', description='plan_description2')]
            )
        ]

        response = self.client.get(
            '/v2/catalog',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header,
                'unknown': 'unknown'
            })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertDictEqual(dict(
            services=[
                dict(
                    id='s1',
                    name='service_name1',
                    description='service_description1',
                    bindable=True,
                    instances_retrievable=False,
                    bindings_retrievable=False,
                    plan_updateable=False,
                    plans=[dict(id='p1', name='default1', description='plan_description1')]
                ),
                dict(
                    id='s2',
                    name='service_name2',
                    description='service_description2',
                    bindable=True,
                    instances_retrievable=False,
                    bindings_retrievable=False,
                    plan_updateable=False,
                    plans=[dict(id='p2', name='default2', description='plan_description2')]
                )
            ]
        ),
            response.json)
