from http import HTTPStatus
from uuid import uuid4

from openbrokerapi import errors
from openbrokerapi.service_broker import GetBindingSpec
from tests import BrokerTestCase


class GetBindingTest(BrokerTestCase):
    def test_returns_200_with_binding_details(self):
        instance_guid = str(uuid4())
        binding_guid = str(uuid4())
        password = str(uuid4())
        parameter = str(uuid4())

        self.broker.get_binding.return_value = GetBindingSpec(
            credentials={"password": password}, parameters={"key": parameter}
        )

        response = self.client.get(
            "/v2/service_instances/{}/service_bindings/{}".format(
                instance_guid, binding_guid
            ),
            headers={"X-Broker-Api-Version": "2.14", "Authorization": self.auth_header},
        )

        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.broker.get_binding.assert_called_once_with(
            instance_id=instance_guid,
            binding_id=binding_guid
        )

        info = response.json
        self.assertDictEqual({"password": password}, info.get("credentials"))
        self.assertDictEqual({"key": parameter}, info.get("parameters"))

    def test_returns_404_if_instance_not_exists(self):
        instance_guid = str(uuid4())
        binding_guid = str(uuid4())

        self.broker.get_binding.side_effect = errors.ErrBindingDoesNotExist()

        response = self.client.get(
            "/v2/service_instances/{}/service_bindings/{}".format(
                instance_guid, binding_guid
            ),
            headers={"X-Broker-Api-Version": "2.14", "Authorization": self.auth_header},
        )

        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertEqual({}, response.json)
