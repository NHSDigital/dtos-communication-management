import json
import message_status_recorder
import pytest


@pytest.fixture
def request_body():
    return {
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
            },
            {
                "attributes": {
                    "messageId": "234",
                    "messageReference": "567",
                    "messageStatus": "sent"
                },
                "meta": {
                    "idempotencyKey": "890"
                }
            }
        ]
    }


def test_save_message_statuses(mocker, request_body):
    """Test saving message statuses to datastore"""
    mock_datastore = mocker.patch("message_status_recorder.datastore")

    assert message_status_recorder.save_message_statuses(request_body) is None

    mock_datastore.create_message_status_record.assert_any_call({
        "details": json.dumps(request_body),
        "idempotency_key": "789",
        "message_id": "123",
        "message_reference": "456",
        "status": "sent"
    })
    mock_datastore.create_message_status_record.assert_any_call({
        "details": json.dumps(request_body),
        "idempotency_key": "890",
        "message_id": "234",
        "message_reference": "567",
        "status": "sent"
    })


def test_message_status_params(request_body):
    """Test conversion of request body to message status parameters"""
    expected = [
        {
            "details": json.dumps(request_body),
            "idempotency_key": "789",
            "message_id": "123",
            "message_reference": "456",
            "status": "sent"
        },
        {
            "details": json.dumps(request_body),
            "idempotency_key": "890",
            "message_id": "234",
            "message_reference": "567",
            "status": "sent"
        }
    ]

    assert message_status_recorder.message_status_params(request_body) == expected


def test_message_status_params_with_missing_field():
    """Test conversion of request body with missing field to message status parameters"""
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

    assert message_status_recorder.message_status_params(request_body) == expected
