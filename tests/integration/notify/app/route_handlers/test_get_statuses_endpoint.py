from app import create_app
import app.services.status_recorder as status_recorder
from app.validators.request_validator import API_KEY_HEADER_NAME, SIGNATURE_HEADER_NAME, CONSUMER_KEY
import pytest
import app.utils.uuid_generator as uuid_generator


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


def test_get_statuses(setup, client, channel_status_post_body):
    """Test that statuses are returned by the endpoint."""
    # Generate message reference using the reference_uuid function
    message_ref = uuid_generator.reference_uuid("4010232137.Thursday 03 February 2022.10:00am")

    # Update the message reference in the channel status post body
    channel_status_post_body["data"][0]["attributes"]["messageReference"] = message_ref

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
