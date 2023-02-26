from http import HTTPStatus
from uuid import uuid4

from openbrokerapi import errors
from openbrokerapi.service_broker import GetInstanceDetailsSpec
from tests import BrokerTestCase


class GetInstanceTest(BrokerTestCase):
    def test_returns_200_with_instance_details(self):
        service_guid = str(uuid4())
        plan_guid = str(uuid4())
        instance_guid = str(uuid4())
        dashboard_url = str(uuid4())
        parameters = str(uuid4())

        self.broker.get_instance.return_value = GetInstanceDetailsSpec(
            service_guid,
            plan_guid,
            dashboard_url=dashboard_url,
            parameters={"key": parameters},
        )

        response = self.client.get(
            "/v2/service_instances/{}".format(instance_guid),
            headers={"X-Broker-Api-Version": "2.14", "Authorization": self.auth_header},
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.broker.get_instance.assert_called_once_with(instance_id=instance_guid)

        info = response.json
        self.assertEqual(service_guid, info.get("service_id"))
        self.assertEqual(plan_guid, info.get("plan_id"))
        self.assertEqual(dashboard_url, info.get("dashboard_url"))
        self.assertDictEqual({"key": parameters}, info.get("parameters"))

    def test_returns_404_if_instance_not_exists(self):
        instance_guid = str(uuid4())

        self.broker.get_instance.side_effect = errors.ErrInstanceDoesNotExist()

        response = self.client.get(
            "/v2/service_instances/{}".format(instance_guid),
            headers={"X-Broker-Api-Version": "2.14", "Authorization": self.auth_header},
        )

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertEqual({}, response.json)

    def test_returns_422_if_instance_is_in_use(self):
        instance_guid = str(uuid4())

        self.broker.get_instance.side_effect = errors.ErrConcurrentInstanceAccess()

        response = self.client.get(
            "/v2/service_instances/{}".format(instance_guid),
            headers={"X-Broker-Api-Version": "2.14", "Authorization": self.auth_header},
        )

        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)
        self.assertEqual(
            response.json,
            {
                "description": "The Service Broker does not support concurrent requests that mutate the same resource.",
                "error": "ConcurrencyError",
            },
        )
