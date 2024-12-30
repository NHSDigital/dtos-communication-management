import azure.functions as func
import function_app
import json
import pytest


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


def create_http_request(payload):
    """Utility function to create an HTTP POST request."""
    return func.HttpRequest(
        method="POST",
        body=bytes(json.dumps(payload).encode("utf-8")),
        url="/api/message-status/create",
    )


def test_main_logs_payload(mocker, payload):
    """Test that the request body is logged when the main function is called."""
    mock_log = mocker.patch("logging.debug")
    request = create_http_request(payload)

    func_call = function_app.main.build().get_user_function()
    func_call(request)

    mock_log.assert_any_call(json.dumps(payload))


def test_main_verify_signature_success(mocker, payload):
    """Test valid headers and signature."""
    mocker.patch("json.loads", return_value=payload)
    mocker.patch("request_verifier.verify_headers", return_value=True)
    mocker.patch("request_verifier.verify_signature", return_value=True)
    mocker.patch("message_status_recorder.save_message_statuses")

    request = create_http_request(payload)
    func_call = function_app.main.build().get_user_function()

    response = func_call(request)

    assert response.status_code == 200
    assert response.get_body().decode("utf-8") == json.dumps({"status": "success"})


def test_main_verify_signature_failure(mocker, payload):
    """Test valid headers but invalid signature."""
    mocker.patch("json.loads", return_value=payload)
    mocker.patch("request_verifier.verify_headers", return_value=True)
    mocker.patch("request_verifier.verify_signature", return_value=False)

    request = create_http_request(payload)
    func_call = function_app.main.build().get_user_function()

    response = func_call(request)

    assert response.status_code == 403
    assert response.get_body().decode("utf-8") == json.dumps({"status": "error"})


def test_main_verify_headers_missing(mocker, payload):
    """Test missing headers."""
    mocker.patch("json.loads", return_value=payload)
    mocker.patch("request_verifier.verify_headers", return_value=False)

    request = create_http_request(payload)
    func_call = function_app.main.build().get_user_function()

    response = func_call(request)

    assert response.status_code == 401
    assert response.get_body().decode("utf-8") == json.dumps({"status": "error"})


def test_health_check():
    """Test health check endpoint."""
    request = func.HttpRequest(method="GET", url="/api/message-status/health-check", body=None)
    func_call = function_app.health_check.build().get_user_function()

    response = func_call(request)

    assert response.status_code == 200
    assert response.get_body().decode("utf-8") == json.dumps({"status": "healthy"})
