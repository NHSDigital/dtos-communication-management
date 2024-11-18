import azure.functions as func
import function_app
import json
import pytest


@pytest.fixture
def payload():
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


def test_main(mocker, payload):
    mock = mocker.patch("logging.info")
    req = func.HttpRequest(
        method="POST",
        body=bytes(json.dumps(payload).encode("utf-8")),
        url="/api/status/callback",
    )

    func_call = function_app.main.build().get_user_function()
    func_call(req)

    mock.assert_called_once()
    mock.assert_called_with(payload)


def test_main_verify_signature(mocker, payload):
    mocker.patch("json.loads", return_value=payload)
    mocker.patch("request_verifier.verify_headers", return_value=True)
    mocker.patch("request_verifier.verify_signature", return_value=True)

    req = func.HttpRequest(
        method="POST",
        body=bytes(json.dumps(payload).encode("utf-8")),
        url="/api/status/callback",
    )

    func_call = function_app.main.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 200
    assert response.get_body().decode("utf-8") == json.dumps({"status": "success"})


def test_main_verify_signature_failure(mocker, payload):
    mocker.patch("json.loads", return_value=payload)
    mocker.patch("request_verifier.verify_headers", return_value=True)
    mocker.patch("request_verifier.verify_signature", return_value=False)

    req = func.HttpRequest(
        method="POST",
        body=bytes(json.dumps(payload).encode("utf-8")),
        url="/api/status/callback",
    )

    func_call = function_app.main.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 403
    assert response.get_body().decode("utf-8") == json.dumps({"status": "error"})


def test_main_verify_headers_missing(mocker, payload):
    mocker.patch("json.loads", return_value=payload)
    mocker.patch("request_verifier.verify_headers", return_value=False)

    req = func.HttpRequest(
        method="POST",
        body=bytes(json.dumps(payload).encode("utf-8")),
        url="/api/status/callback",
    )

    func_call = function_app.main.build().get_user_function()
    response = func_call(req)

    assert response.status_code == 401
    assert response.get_body().decode("utf-8") == json.dumps({"status": "error"})
