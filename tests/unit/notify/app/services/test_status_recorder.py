import json
import app.services.status_recorder as status_recorder


def test_save_statuses_with_channel_status_data(mocker, channel_status_post_body):
    """Test saving channel status data to datastore"""
    mock_datastore = mocker.patch("app.services.status_recorder.datastore")

    assert status_recorder.save_statuses(channel_status_post_body)

    mock_datastore.create_status_record.assert_called_once_with("ChannelStatus", {
        "details": json.dumps(channel_status_post_body),
        "idempotency_key": "2515ae6b3a08339fba3534f3b17cd57cd573c57d25b25b9aae08e42dc9f0a445", #gitleaks:allow
        "message_id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
        "message_reference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
        "status": "delivered"
    })


def test_save_statuses_with_message_status_data(mocker, message_status_post_body):
    """Test saving message status data to datastore"""
    mock_datastore = mocker.patch("app.services.status_recorder.datastore")

    assert status_recorder.save_statuses(message_status_post_body)

    mock_datastore.create_status_record.assert_called_once_with("MessageStatus", {
        "details": json.dumps(message_status_post_body),
        "idempotency_key": "2515ae6b3a08339fba3534f3b17cd57cd573c57d25b25b9aae08e42dc9f0a445", #gitleaks:allow
        "message_id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
        "message_reference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
        "status": "sending"
    })


def test_status_params(message_status_post_body):
    """Test conversion of request body to message status parameters"""
    expected = [
        {
            "details": json.dumps(message_status_post_body),
            "idempotency_key": "2515ae6b3a08339fba3534f3b17cd57cd573c57d25b25b9aae08e42dc9f0a445", #gitleaks:allow
            "message_id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
            "message_reference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
            "status": "sending"
        },
    ]

    assert status_recorder.status_params(message_status_post_body) == expected


def test_status_params_with_missing_field(message_status_post_body):
    """Test conversion of request body with missing field to message status parameters"""
    message_status_post_body["data"][0]["attributes"].pop("messageReference")

    expected = []

    assert status_recorder.status_params(message_status_post_body) == expected
