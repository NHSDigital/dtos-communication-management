import time
import uuid
from unittest.mock import MagicMock
from functions.batch_notify.message_batch_body import MessageBatchBody


class TestMessageBatchBody():
    def test_call(self):
        mock_reference_uuid = MagicMock(name="refererence_uuid")
        mock_reference_uuid.return_value = str(uuid.uuid4())
        MessageBatchBody.reference_uuid = mock_reference_uuid
        routing_plan_id = str(uuid.uuid4())

        iterable = [
                {"nhs_number": "0000000000", "date_of_birth": "1990-01-02"},
                {"nhs_number": "1111111111", "date_of_birth": "2001-12-22"},
            ]

        actual = MessageBatchBody.call(routing_plan_id, iterable)

        expected = {
            "data": {
                "type": "MessageBatch",
                "attributes": {
                    "messageBatchReference": MessageBatchBody.reference_uuid(time.time()),
                    "routingPlanId": routing_plan_id,
                    "messages": [
                        {
                            "messageReference": MessageBatchBody.reference_uuid("0000000000"),
                            "recipient": {
                                "nhsNumber": "0000000000",
                                "dateOfBirth": "1990-01-02",
                            },
                            "personalisation": {},
                        },
                        {
                            "messageReference": MessageBatchBody.reference_uuid("1111111111"),
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
