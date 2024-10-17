import json
import pytest
import requests_mock
import uuid

from unittest.mock import MagicMock
from functions.batch_notify.message_batch import MessageBatch
from functions.batch_notify.message_batch_body import MessageBatchBody


class TestMessageBatch:
    @pytest.fixture
    def setup(self):
        mock_base_url = MagicMock(name="base_url")
        mock_base_url.return_value = "http://example.com"
        MessageBatch.base_url = mock_base_url

        mock_reference_uuid = MagicMock(name="refererence_uuid")
        mock_reference_uuid.return_value = str(uuid.uuid4())
        MessageBatchBody.reference_uuid = mock_reference_uuid

    def test_call(self, setup):
        routing_plan = "breast-screening-pilot"
        routing_plan_id = MessageBatch.ROUTING_PLANS[routing_plan]
        patient_data = [
            {"nhs_number": "0000000000", "date_of_birth": "1981-10-07"},
        ]
        message_batch_data = {
            "routing_plan": routing_plan,
            "data": patient_data,
        }
        response_text = json.dumps({
            "data": {
                "type": "MessageBatch",
                "id": "2nZnxW4nTuQr2OTiuhm1pNpAQTp",
                "attributes": {
                    "messageBatchReference": "03167672-669e-4950-b656-ebdb83fc62ff",
                    "routingPlan": {
                        "id": routing_plan_id,
                        "version": "1"
                    }
                }
            }
        })

        with requests_mock.Mocker() as rm:
            adapter = rm.post('http://example.com/comms/v1/message-batches', text=response_text)
            actual_response = MessageBatch.call(message_batch_data)
            expected_request_body = MessageBatchBody.call(routing_plan_id, patient_data)

            assert adapter.called
            assert adapter.call_count == 1
            assert adapter.last_request.json() == expected_request_body

    def test_url(self, setup):
        assert MessageBatch.url() == "http://example.com/comms/v1/message-batches"
