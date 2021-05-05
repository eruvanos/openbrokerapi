import http

from openbrokerapi.service_broker import LastOperation, OperationState
from tests import BrokerTestCase


class LastBindingOperationTest(BrokerTestCase):
    def setUp(self):
        self.broker.service_id.return_value = 'service-guid-here'

    def test_last_operation_called_just_with_required_fields(self):
        self.broker.last_binding_operation.return_value = LastOperation(OperationState.IN_PROGRESS, 'Running...')

        self.client.get(
            '/v2/service_instances/here-instance_id/service_bindings/binding_id/last_operation',
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.broker.last_binding_operation.assert_called_once_with('here-instance_id', 'binding_id', None, None, None)

    def test_last_operation_called_with_operation_data(self):
        self.broker.last_binding_operation.return_value = LastOperation(OperationState.IN_PROGRESS, 'Running...')

        query = 'service_id=&plan_id=456&operation=service-guid-here%20operation-data'
        self.client.get(
            '/v2/service_instances/here-instance_id/service_bindings/binding_id/last_operation?%s' % query,
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.broker.last_binding_operation.assert_called_once_with('here-instance_id', 'binding_id',
                                                                   'service-guid-here operation-data', "", "456")

    def test_returns_200_with_given_state(self):
        self.broker.last_binding_operation.return_value = LastOperation(OperationState.IN_PROGRESS, 'Running...')

        query = 'service_id=123&plan_id=456&operation=service-guid-here%20operation-data'
        response = self.client.get(
            '/v2/service_instances/here-instance_id/service_bindings/binding_id/last_operation?%s' % query,
            headers={
                'X-Broker-Api-Version': '2.13',
                'Authorization': self.auth_header
            })

        self.broker.last_binding_operation.assert_called_once_with('here-instance_id', 'binding_id',
                                                                   'service-guid-here operation-data', "123", "456")
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.json, dict(
            state=OperationState.IN_PROGRESS.value,
            description='Running...'
        ))
