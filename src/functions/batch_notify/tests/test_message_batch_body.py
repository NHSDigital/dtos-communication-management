import time
import uuid
from batch_notify.message_batch_body import message_batch_body
from batch_notify.message_batch_body import reference_uuid


class TestMessageBatchBody():
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
