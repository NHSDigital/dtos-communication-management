import json
import pytest
import requests_mock
import time
import uuid

from batch_notify.helper import send_message_batch
from batch_notify.helper import ROUTING_PLANS
from batch_notify.helper import message_batch_body
from batch_notify.helper import reference_uuid


class TestHelper:
    @pytest.fixture
    def setup(self, monkeypatch):
        def mock_uuid4(_val):
            return "03167672-669e-4950-b656-ebdb83fc62ff"

        monkeypatch.setenv("BASE_URL", "http://example.com")
        monkeypatch.setattr("batch_notify.helper.reference_uuid", mock_uuid4)

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

    def test_message_batch_body(self, monkeypatch):
        def mock_time():
            return "1234567890"
        monkeypatch.setattr(time, "time", mock_time)
        routing_plan_id = str(uuid.uuid4())

        iterable = [
                {"nhs_number": "0000000000", "date_of_birth": "1990-01-02"},
                {"nhs_number": "1111111111", "date_of_birth": "2001-12-22"},
            ]

        actual = message_batch_body(routing_plan_id, iterable)

        expected = {
            "data": {
                "type": "MessageBatch",
                "attributes": {
                    "messageBatchReference": reference_uuid(time.time()),
                    "routingPlanId": routing_plan_id,
                    "messages": [
                        {
                            "messageReference": reference_uuid("0000000000"),
                            "recipient": {
                                "nhsNumber": "0000000000",
                                "dateOfBirth": "1990-01-02",
                            },
                            "personalisation": {},
                        },
                        {
                            "messageReference": reference_uuid("1111111111"),
                            "recipient": {
                                "nhsNumber": "1111111111",
                                "dateOfBirth": "2001-12-22",
                            },
                            "personalisation": {},
                        },
                    ],
                },
            }
        }

        assert actual == expected
