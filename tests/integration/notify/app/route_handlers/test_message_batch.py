from app import create_app
from app.validators.request_validator import CONSUMER_KEY_NAME
import pytest
import requests_mock


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv("NOTIFY_API_URL", "http://example.com")


@pytest.fixture
def client():
    app = create_app()
    yield app.test_client()


def test_message_batch_succeeds(setup, client, message_batch_post_body, message_batch_post_response, consumer):
    """Test that valid auth header and payload succeeds."""

    headers = {
        "Authorization": "Bearer client_token",
        CONSUMER_KEY_NAME: consumer.key
    }

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
    """Test that the supplied auth header is preserved in the request to the Notify API."""

    headers = {
        "Authorization": "Bearer client_token",
        CONSUMER_KEY_NAME: "some-consumer"
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


def test_message_batch_fails_with_invalid_auth_header(setup, client, message_batch_post_body):
    """Test that invalid Bearer token fails authentication."""
    headers = {
        "Authorization": "some_invalid_value",
        CONSUMER_KEY_NAME: "some-consumer"
    }

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/message-batches",
            status_code=401,
            json={"status": "failed", "error": "Unauthorized"}
        )

        response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

        assert response.status_code == 401
        assert adapter.last_request.headers["Authorization"] == "Bearer invalid"


def test_message_batch_fails_with_missing_auth_header(setup, client, message_batch_post_body):
    """Test that missing auth header fails authentication."""
    headers = {
        CONSUMER_KEY_NAME: "some-consumer"
    }

    with requests_mock.Mocker() as rm:
        adapter = rm.post(
            "http://example.com/comms/v1/message-batches",
            status_code=401,
            json={"status": "failed", "error": "Authorization header not present"}
        )

        response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

        assert response.status_code == 401
        assert response.get_json() == {"status": "failed", "error": "Authorization header not present"}

def test_message_batch_fails_with_missing_consumer_header(setup, client, message_batch_post_body):
    """Test that missing auth header fails authentication."""
    headers = {
        "Authorization": "Bearer client_token",
    }

    response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

    assert response.status_code == 401
    assert response.get_json() == {"status": "failed", "error": "Consumer Key header not present"}

def test_message_batch_fails_with_nonexistent_consumer_header(setup, client, message_batch_post_body):
    """Test that missing auth header fails authentication."""
    headers = {
        "Authorization": "Bearer client_token",
        CONSUMER_KEY_NAME: "invalid-consumer"
    }

    response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

    assert response.status_code == 401
    assert response.get_json() == {"status": "failed", "error": "Consumer not valid"}

def test_message_batch_fails_with_invalid_post_body(setup, client, message_batch_post_body):
    """Test that invalid request body fails schema validation."""
    message_batch_post_body["data"]["type"] = "invalid"

    headers = {
        "Authorization": "Bearer client_token",
        CONSUMER_KEY_NAME: "some-consumer"
    }

    response = client.post('/api/message/batch', json=message_batch_post_body, headers=headers)

    assert response.status_code == 422
    assert response.get_json() == {"status": "failed", "error": "Invalid body: 'invalid'"}
