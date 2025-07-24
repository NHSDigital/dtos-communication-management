import app.cache as cache
import app.services.consumer_fetcher as fetcher
import app.validators.request_validator as request_validator
import app.utils.hmac_signature as hmac_signature
import json
import pytest


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('CLIENT_API_KEY', 'client_api_key')
    monkeypatch.setenv('NOTIFY_API_KEY', 'notify_api_key')


def test_verify_signature_invalid():
    """Test that an invalid signature fails verification."""
    headers = {request_validator.SIGNATURE_HEADER_NAME: 'signature'}
    body = {'data': 'body'}

    assert not request_validator.verify_signature(headers, body, 'invalid_signature')


def test_verify_signature_valid():
    """Test that a valid signature passes verification."""
    body = {'data': 'body'}
    signature = hmac_signature.create_digest('application_id.notify_api_key', json.dumps(body))

    headers = {request_validator.SIGNATURE_HEADER_NAME: signature}
    assert request_validator.verify_signature(headers, body, 'application_id.notify_api_key')


def test_verify_headers_missing_all():
    """Test that missing all headers fails verification."""
    headers = {}
    assert request_validator.verify_headers(headers) == (False, 'Missing Authorization header')


def test_verify_headers_missing_api_key():
    """Test that missing API key header fails verification."""
    headers = {
        request_validator.AUTHORIZATION_HEADER_NAME: 'Bearer token',
        request_validator.SIGNATURE_HEADER_NAME: 'signature'
    }
    assert request_validator.verify_headers(headers) == (False, 'Missing API key header')



def test_verify_headers_invalid_api_key():
    """Test that an invalid API key fails verification."""
    headers = {
        request_validator.AUTHORIZATION_HEADER_NAME: 'Bearer token',
        request_validator.API_KEY_HEADER_NAME: 'invalid_api_key'
    }
    assert request_validator.verify_headers(headers) == (False, 'Invalid API key')


def test_verify_get_headers_for_missing_auth():
    """Test that valid headers pass verification."""
    headers = {
        request_validator.API_KEY_HEADER_NAME: 'api_key',
        request_validator.CONSUMER_KEY_NAME: 'some-key'
    }
    assert request_validator.verify_headers(
        headers) == (False, "Missing Authorization header")


def test_verify_headers_missing_consumer():
    """Test that valid headers pass verification."""
    headers = {
        request_validator.AUTHORIZATION_HEADER_NAME: 'Bearer token',
        request_validator.API_KEY_HEADER_NAME: 'client_api_key',
    }
    assert request_validator.verify_headers(
        headers) == (False, "Missing Consumer key header")


def test_verify_headers_for_consumers_valid(app, consumer):
    """Test that valid headers pass verification."""
    headers = {
        request_validator.AUTHORIZATION_HEADER_NAME: 'Bearer token',
        request_validator.API_KEY_HEADER_NAME: 'client_api_key',
        request_validator.CONSUMER_KEY_NAME: 'some-consumer'
    }
    assert request_validator.verify_headers(
        headers) == (True, "")


def test_verify_headers_consumer_not_found(app):
    """Test that a Consumer is not found with an invalid consumer_key"""
    headers = {
        request_validator.AUTHORIZATION_HEADER_NAME: 'Bearer token',
        request_validator.API_KEY_HEADER_NAME: 'client_api_key',
        request_validator.CONSUMER_KEY_NAME: 'not-a-consumer'
    }
    assert request_validator.verify_headers(
        headers) == (False, "Invalid Consumer key")


def test_verify_callback_headers_missing_api_key():
    """Test that missing signature header fails verification."""
    headers = {
        request_validator.SIGNATURE_HEADER_NAME: 'signature',
    }
    assert request_validator.verify_callback_headers(headers) == (False, 'Missing API key header')


def test_verify_callback_headers_missing_signature():
    """Test that missing signature header fails verification."""
    headers = {
        request_validator.API_KEY_HEADER_NAME: 'notify_api_key'
    }
    assert request_validator.verify_callback_headers(headers) == (False, 'Missing signature header')


def test_verify_callback_headers_valid():
    """Test that valid API key and signature headers pass verification."""
    headers = {
        request_validator.SIGNATURE_HEADER_NAME: 'signature',
        request_validator.API_KEY_HEADER_NAME: 'notify_api_key',
    }
    assert request_validator.verify_callback_headers(headers) == (True, "")
