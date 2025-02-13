from app import create_app
import app.services.status_recorder as status_recorder
from app.validators.request_validator import API_KEY_HEADER_NAME, SIGNATURE_HEADER_NAME, signature_secret
import json
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


def test_get_statuses_request_validation_fails(setup, client, message_status_post_body):
    """Test that invalid request header values fail HMAC signature validation."""
    headers = {API_KEY_HEADER_NAME: "not_the_api_key", SIGNATURE_HEADER_NAME: "signature"}

    response = client.get('/api/statuses', headers=headers)

    assert response.status_code == 401
    assert response.get_json() == {"status": "Invalid API key"}


def test_get_statuses(setup, client, channel_status_post_body):
    """Test that statuses are returned by the endpoint."""
    status_recorder.save_statuses(channel_status_post_body)
    query_params = {
        "channel": "nhsapp",
        "channelStatus": "delivered",
    }

    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: "signature"}

    response = client.get('/api/statuses', query_string=query_params, headers=headers)

    assert response.status_code == 200
