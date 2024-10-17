import json
import pytest
import requests_mock
import uuid

from batch_notify.message_batch import send_message_batch
from batch_notify.message_batch import ROUTING_PLANS
from batch_notify.message_batch_body import message_batch_body


class TestMessageBatch:
    @pytest.fixture
    def setup(self, monkeypatch):
        def mock_uuid4(_val):
            return "03167672-669e-4950-b656-ebdb83fc62ff"

        monkeypatch.setenv("BASE_URL", "http://example.com")
        monkeypatch.setattr("batch_notify.message_batch_body.reference_uuid", mock_uuid4)

    def test_send_message_batch(self, setup):
        routing_plan = "breast-screening-pilot"
        routing_plan_id = ROUTING_PLANS[routing_plan]
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
            send_message_batch(message_batch_data)
            expected_request_body = message_batch_body(routing_plan_id, patient_data)

            assert adapter.called
            assert adapter.call_count == 1
            assert adapter.last_request.json() == expected_request_body
