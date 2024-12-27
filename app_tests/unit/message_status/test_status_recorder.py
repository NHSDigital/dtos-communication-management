import json
import app.services.message_status.status_recorder as status_recorder
import pytest


@pytest.fixture
def message_status_data():
    return {
        "data": [
            {

                "type": "messageStatus",
                "attributes": {
                    "messageId": "123",
                    "messageReference": "eb4c7f1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
                    "messageStatus": "sent"
                },
                "meta": {
                    "idempotencyKey": "789"
                }
            },
            {
                "type": "messageStatus",
                "attributes": {
                    "messageId": "234",
                    "messageReference": "0c3b3b1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
                    "messageStatus": "delivered"
                },
                "meta": {
                    "idempotencyKey": "890"
                }
            }
        ]
    }


@pytest.fixture
def channel_status_data():
    return {
        "data": [
            {
                "type": "channelStatus",
                "attributes": {
                    "channel": "nhsapp",
                    "channelStatus": "read",
                    "messageId": "234",
                    "messageReference": "0c3b3b1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
                },
                "meta": {
                    "idempotencyKey": "789"
                }
            }
        ]
    }


def test_save_message_statuses(mocker, message_status_data):
    """Test saving message statuses to datastore"""
    mock_datastore = mocker.patch("app.services.message_status.status_recorder.datastore")

    assert status_recorder.save_statuses(message_status_data) is None

    mock_datastore.create_status_record.assert_any_call({
        "details": json.dumps(message_status_data["data"][0]),
        "idempotency_key": "789",
        "message_id": "123",
        "message_reference": "eb4c7f1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
        "status": "sent"
    }, False)
    mock_datastore.create_status_record.assert_any_call({
        "details": json.dumps(message_status_data["data"][1]),
        "idempotency_key": "890",
        "message_id": "234",
        "message_reference": "0c3b3b1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
        "status": "delivered"
    }, False)


def test_message_status_params(message_status_data):
    """Test conversion of request body to message status parameters"""
    assert status_recorder.status_params(message_status_data["data"][0]) == {
        "details": json.dumps(message_status_data["data"][0]),
        "idempotency_key": "789",
        "message_id": "123",
        "message_reference": "eb4c7f1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
        "status": "sent"
    }
    assert status_recorder.status_params(message_status_data["data"][1]) == {
        "details": json.dumps(message_status_data["data"][1]),
        "idempotency_key": "890",
        "message_id": "234",
        "message_reference": "0c3b3b1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
        "status": "delivered"
    }


def test_status_params_with_missing_field():
    """Test conversion of request body with missing field to message status parameters"""
    incomplete_data = {
        "data": [
            {
                "attributes": {
                    "messageId": "123",
                    "messageReference": "eb4c7f1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
                    "messageStatus": "sent"
                },
                "meta": {}
            }
        ]
    }

    assert status_recorder.status_params(incomplete_data) is None


def test_save_channel_statuses(mocker, channel_status_data):
    """Test saving channel statuses to datastore"""
    mock_datastore = mocker.patch("app.services.message_status.status_recorder.datastore")

    assert status_recorder.save_statuses(channel_status_data) is None

    mock_datastore.create_status_record.assert_called_once_with({
        "details": json.dumps(channel_status_data["data"][0]),
        "idempotency_key": "789",
        "message_id": "234",
        "message_reference": "0c3b3b1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
        "status": "read"
    }, True)


def test_channel_status_params(channel_status_data):
    """Test conversion of request body to channel status parameters"""
    assert status_recorder.status_params(channel_status_data["data"][0]) == {
        "details": json.dumps(channel_status_data["data"][0]),
        "idempotency_key": "789",
        "message_id": "234",
        "message_reference": "0c3b3b1e-7f3d-4b62-8b0d-1b1f5b3b6b6d",
        "status": "read"
    }

