from app import create_app
from app.validators.request_validator import API_KEY_HEADER_NAME, SIGNATURE_HEADER_NAME, signature_secret
from datetime import datetime, timedelta
import app.models as models
import app.utils.database as database
import app.utils.hmac_signature as hmac_signature
import json
import pytest
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('NOTIFY_API_KEY', 'api_key')


@pytest.fixture
def client():
    app = create_app()
    yield app.test_client()


def test_status_create_request_validation_fails(setup, client, message_status_post_body):
    """Test that invalid request header values fail HMAC signature validation."""
    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: "signature"}

    response = client.post('/api/status/create', json=message_status_post_body, headers=headers)

    assert response.status_code == 403
    assert response.get_json() == {"status": "Invalid signature"}


def test_status_create_body_validation_fails(setup, client, message_status_post_body):
    """Test that invalid request body fails schema validation."""
    message_status_post_body["data"][0]["attributes"]["messageStatus"] = "invalid"
    signature = hmac_signature.create_digest(signature_secret(), json.dumps(message_status_post_body, sort_keys=True))

    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: signature}

    response = client.post('/api/status/create', json=message_status_post_body, headers=headers)

    assert response.status_code == 422
    assert response.get_json() == {"status": "'invalid' is not one of ['created', 'pending_enrichment', 'enriched', 'sending', 'delivered', 'failed']"}


def test_status_create_request_validation_succeeds(setup, client, message_status_post_body):
    """Test that valid request header values pass HMAC signature validation."""
    signature = hmac_signature.create_digest(signature_secret(), json.dumps(message_status_post_body, sort_keys=True))

    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: signature}

    response = client.post('/api/status/create', json=message_status_post_body, headers=headers)

    assert response.status_code == 200
    assert response.get_json() == {"status": "success"}


def test_status_create_saves_records(setup, client, message_status_post_body):
    """Test that valid requests are saved to the database."""
    signature = hmac_signature.create_digest(signature_secret(), json.dumps(message_status_post_body, sort_keys=True))

    headers = {API_KEY_HEADER_NAME: "api_key", SIGNATURE_HEADER_NAME: signature}

    response = client.post('/api/status/create', json=message_status_post_body, headers=headers)

    assert response.status_code == 200

    with Session(database.engine()) as session:
        status_record = session.scalars(select(models.MessageStatus)).all()[0]
        assert status_record.created_at - datetime.now() < timedelta(seconds=1)
        assert status_record.details == message_status_post_body
        assert status_record.idempotency_key == message_status_post_body["data"][0]["meta"]["idempotencyKey"]
        assert status_record.message_id == message_status_post_body["data"][0]["attributes"]["messageId"]
        assert str(status_record.message_reference) == message_status_post_body["data"][0]["attributes"]["messageReference"]
        assert status_record.status == models.MessageStatuses(message_status_post_body["data"][0]["attributes"]["messageStatus"])
