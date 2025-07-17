from app import create_app
import app.services.status_recorder as status_recorder
from app.validators.request_validator import API_KEY_HEADER_NAME, SIGNATURE_HEADER_NAME, CONSUMER_KEY
import pytest


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('CLIENT_API_KEY', 'api_key')
    monkeypatch.setenv('NOTIFY_API_KEY', 'api_key')


@pytest.fixture
def client():
    app = create_app()
    yield app.test_client()


def test_get_statuses_request_validation_fails_on_api_key(setup, client, message_status_post_body):
    """Test that invalid request header values fail HMAC signature validation."""
    headers = {API_KEY_HEADER_NAME: "not_the_api_key", SIGNATURE_HEADER_NAME: "signature"}

    response = client.get('/api/statuses', headers=headers)

    assert response.status_code == 401
    assert response.get_json() == {"status": "Invalid API key"}

def test_get_statuses_request_validation_fails_on_missing_consumer(setup, client, message_status_post_body):
    """Test that invalid request header values fail HMAC signature validation."""
    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: "signature"}

    response = client.get('/api/statuses', headers=headers)

    assert response.status_code == 401
    assert response.get_json() == {"status": "Missing Consumer key header"}


def test_get_statuses_request_validation_fails_on_invalid_consumer(setup, client, message_status_post_body):
    """Test that invalid request header values fail signature validation."""
    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: "signature", CONSUMER_KEY: "not-a-consumer"}

    response = client.get('/api/statuses', headers=headers)

    assert response.status_code == 401
    assert response.get_json() == {"status": "Consumer not valid"}


def test_get_statuses(setup, client, channel_status_post_body, message_batch_post_response, message_batch):
    """Test that statuses are returned by the endpoint."""
    # Generate message reference from test fixture
    message = message_batch_post_response["data"]["attributes"]["messages"][0]
    message_ref = message["messageReference"]

    # Update the message reference in the channel status post body
    channel_status_post_body["data"][0]["attributes"]["messageReference"] = message_ref
    channel_status_post_body["data"][0]["attributes"]["messageId"] = message["id"]

    status_recorder.save_statuses(channel_status_post_body)
    query_params = {
        "channel": "nhsapp",
        "supplierStatus": "read",
    }

    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: "signature", CONSUMER_KEY: "some-consumer"}

    response = client.get('/api/statuses', query_string=query_params, headers=headers)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert len(response_json["data"]) == 1
    assert response_json["data"][0]["channel"] == "nhsapp"
    assert response_json["data"][0]["channelStatus"] == "delivered"
    assert response_json["data"][0]["supplierStatus"] == "read"
    assert response_json["data"][0]["message_id"] == "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
    assert response_json["data"][0]["message_reference"] == message_ref
