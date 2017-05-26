import http

from werkzeug.wrappers import Response

from test import BrokerTestCase
from openbrokerapi.service_broker import LastOperation, OperationState


class LastOperationTest(BrokerTestCase):

    def test_last_operation_called_just_with_required_fields(self):
        self.broker.last_operation.return_value = LastOperation(OperationState.IN_PROGRESS, "Running...")

        _ = self.client.get(
            "/v2/service_instances/here-instance_id/last_operation",
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.broker.last_operation.assert_called_once_with("here-instance_id", None)

    def test_last_operation_called_with_the_right_values(self):
        self.broker.last_operation.return_value = LastOperation(OperationState.IN_PROGRESS, "Running...")

        query = "service_id=123&plan_id=456&operation=operation-data"
        _ = self.client.get(
            "/v2/service_instances/here-instance_id/last_operation?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.broker.last_operation.assert_called_once_with("here-instance_id", "operation-data")



    def test_returns_200_with_given_state(self):
        self.broker.last_operation.return_value = LastOperation(OperationState.IN_PROGRESS, "Running...")

        query = "service_id=123&plan_id=456&operation=operation-data"
        response: Response = self.client.get(
            "/v2/service_instances/here-instance_id/last_operation?%s" % query,
            headers={
                'X-Broker-Api-Version': '2.00',
                'Authorization': self.auth_header
            })

        self.assertEquals(response.status_code, http.HTTPStatus.OK)
        self.assertEquals(response.json, dict(
            state=OperationState.IN_PROGRESS.value,
            description="Running..."
        ))
