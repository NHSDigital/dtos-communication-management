import json
import request_body_processor


def test_message_status_params():
    request_body = {
        "data": [
            {
                "attributes": {
                    "messageId": "123",
                    "messageReference": "456",
                    "messageStatus": "sent"
                },
                "meta": {
                    "idempotencyKey": "789"
                }
            }
        ]
    }

    expected = [
        {
            "details": json.dumps(request_body),
            "idempotency_key": "789",
            "message_id": "123",
            "message_reference": "456",
            "status": "sent"
        }
    ]

    assert request_body_processor.message_status_params(request_body) == expected

def test_message_status_params_with_missing_field():
    request_body = {
        "data": [
            {
                "attributes": {
                    "messageId": "123",
                    "messageReference": "456",
                    "messageStatus": "sent"
                },
                "meta": {}
            }
        ]
    }

    expected = []

    assert request_body_processor.message_status_params(request_body) == expected

