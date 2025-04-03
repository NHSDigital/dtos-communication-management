from app import create_app
from app.validators.request_validator import API_KEY_HEADER_NAME, SIGNATURE_HEADER_NAME
import app.utils.hmac_signature as hmac_signature
import json
import os
import pytest
import requests_mock


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('CLIENT_APPLICATION_ID', 'application_id')
    monkeypatch.setenv('CLIENT_API_KEY', 'api_key')
    monkeypatch.setenv("NOTIFY_API_URL", "http://example.com")


@pytest.fixture
def client():
    app = create_app()
    yield app.test_client()


def test_message_batch_request_validation_fails(setup, client, message_batch_post_body):
    """Test that invalid request header values fail HMAC signature validation."""
    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: "signature"}

    response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

    assert response.status_code == 403
    assert response.get_json() == {"status": "failed", "error": "Invalid signature"}


def test_message_batch_succeeds(setup, client, message_batch_post_body, message_batch_post_response):
    """Test that valid request header values pass HMAC signature validation."""
    signature = hmac_signature.create_digest(
        f"{os.getenv('CLIENT_APPLICATION_ID')}.{os.getenv('CLIENT_API_KEY')}",
        json.dumps(message_batch_post_body, sort_keys=True)
    )

    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: signature}

    with requests_mock.Mocker() as rm:
        rm.post(
            "http://example.com/comms/v1/message-batches",
            status_code=201,
            json=message_batch_post_response
        )

        response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

        assert response.status_code == 201
        assert response.get_json() == {"status": "success", "response": message_batch_post_response}


def test_message_batch_preserves_auth_header(setup, client, message_batch_post_body, message_batch_post_response):
    """Test that valid request header values pass HMAC signature validation."""
    signature = hmac_signature.create_digest(
        f"{os.getenv('CLIENT_APPLICATION_ID')}.{os.getenv('CLIENT_API_KEY')}",
        json.dumps(message_batch_post_body, sort_keys=True)
    )

    headers = {
        API_KEY_HEADER_NAME: "api_key",
        "Authorization": "Bearer client_token",
        SIGNATURE_HEADER_NAME: signature,
    }

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/message-batches",
            status_code=201,
            json=message_batch_post_response
        )

        response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

        assert response.status_code == 201
        assert adapter.last_request.headers["Authorization"] == "Bearer client_token"



def test_message_batch_fails_with_invalid_post_body(setup, client, message_batch_post_body):
    """Test that invalid request body fails schema validation."""
    message_batch_post_body["data"]["type"] = "invalid"
    signature = hmac_signature.create_digest(
        f"{os.getenv('CLIENT_APPLICATION_ID')}.{os.getenv('CLIENT_API_KEY')}",
        json.dumps(message_batch_post_body, sort_keys=True)
    )

    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: signature}

    response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

    assert response.status_code == 422
    assert response.get_json() == {"status": "failed", "error": "Invalid body: 'invalid'"}
