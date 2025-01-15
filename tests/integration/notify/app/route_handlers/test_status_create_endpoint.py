from app import create_app
from app.validators.request_validator import API_KEY_HEADER_NAME, SIGNATURE_HEADER_NAME, signature_secret
import hashlib
import hmac
import json
import pytest


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('NOTIFY_API_KEY', 'api_key')


@pytest.fixture
def client():
    app = create_app()
    yield app.test_client()


def test_status_create_request_validation_fails(setup, client):
    """Test that invalid request header values fail HMAC signature validation."""
    data = {"some": "data"}
    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: "signature"}

    response = client.post('/api/status/create', data=data, headers=headers)

    assert response.status_code == 403
    assert response.get_json() == {"status": "error"}


def test_status_create_request_validation_succeeds(setup, client):
    """Test that valid request header values pass HMAC signature validation."""
    data = {"some": "data"}
    signature = hmac.new(
        bytes(signature_secret(), 'ASCII'),
        msg=bytes(json.dumps(data), 'ASCII'),
        digestmod=hashlib.sha256
    ).hexdigest()
    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: signature}

    response = client.post('/api/status/create', data=data, headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"status": "success"}
