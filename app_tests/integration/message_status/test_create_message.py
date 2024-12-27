import json
import pytest
from app.services.message_status.main import create_message_status


@pytest.fixture
def payload():
    """Sample payload used across test cases."""
    return {
        "data": [
            {
                "type": "MessageStatus",
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
                    "messageStatus": "sending",
                    "messageStatusDescription": " ",
                    "channels": [
                        {
                            "type": "email",
                            "channelStatus": "delivered"
                        }
                    ],
                    "timestamp": "2023-11-17T14:27:51.413Z",
                    "routingPlan": {
                        "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                        "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp"
                    }
                }
            }
        ]
    }


def test_main_logs_payload(mocker, payload):
    """Test that the request body is logged when the main function is called."""
    mock_log = mocker.patch("logging.debug")

    req_body = json.dumps(payload)
    headers = {}

    _, status_code = create_message_status(req_body, headers)

    assert status_code == 401
    mock_log.assert_any_call(req_body)


def test_main_verify_signature_success(mocker, payload):
    """Test valid headers and signature."""
    mock_verify_headers = mocker.patch("app.services.message_status.request_verifier.verify_headers", return_value=True)
    mock_verify_signature = mocker.patch("app.services.message_status.request_verifier.verify_signature", return_value=True)
    mock_save_statuses = mocker.patch("app.services.message_status.status_recorder.save_statuses")

    req_body = json.dumps(payload)
    headers = {"Authorization": "valid-signature"}

    response, status_code = create_message_status(req_body, headers)

    assert status_code == 200
    assert response == {"status": "success"}
    mock_save_statuses.assert_called_once_with(payload)


def test_main_verify_signature_failure(mocker, payload):
    """Test valid headers but invalid signature."""
    mock_verify_headers = mocker.patch("app.services.message_status.request_verifier.verify_headers", return_value=True)
    mock_verify_signature = mocker.patch("app.services.message_status.request_verifier.verify_signature", return_value=False)

    req_body = json.dumps(payload)
    headers = {"Authorization": "invalid-signature"}

    response, status_code = create_message_status(req_body, headers)

    assert status_code == 403
    assert response == {"status": "error"}


def test_main_verify_headers_missing(mocker, payload):
    """Test missing headers."""
    mock_verify_headers = mocker.patch("app.services.message_status.request_verifier.verify_headers", return_value=False)

    req_body = json.dumps(payload)
    headers = {}

    response, status_code = create_message_status(req_body, headers)

    assert status_code == 401
    assert response == {"status": "error"}
