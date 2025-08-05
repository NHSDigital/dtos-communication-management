from app.queries.consumer import fetch_all_cached
import app.validators.request_validator as request_validator
import app.utils.hmac_signature as hmac_signature
import json
import pytest


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('NOTIFY_API_KEY', 'api_key')
    fetch_all_cached.cache_clear()


def test_verify_signature_invalid(setup):
    """Test that an invalid signature fails verification."""
    headers = {request_validator.SIGNATURE_HEADER_NAME: 'signature'}
    body = {'data': 'body'}

    assert not request_validator.verify_signature(headers, body, 'invalid_signature')


def test_verify_signature_valid(setup):
    """Test that a valid signature passes verification."""
    body = {'data': 'body'}
    signature = hmac_signature.create_digest('application_id.api_key', json.dumps(body))

    headers = {request_validator.SIGNATURE_HEADER_NAME: signature}
    assert request_validator.verify_signature(headers, body, 'application_id.api_key')


def test_verify_headers_missing_all(setup):
    """Test that missing all headers fails verification."""
    headers = {}
    assert request_validator.verify_headers(headers, 'api_key') == (False, 'Missing API key header')


def test_verify_headers_missing_api_key(setup):
    """Test that missing API key header fails verification."""
    headers = {request_validator.SIGNATURE_HEADER_NAME: 'signature'}
    assert request_validator.verify_headers(headers, 'api_key') == (False, 'Missing API key header')


def test_verify_headers_missing_signature(setup):
    """Test that missing signature header fails verification."""
    headers = {request_validator.API_KEY_HEADER_NAME: 'api_key'}
    assert request_validator.verify_headers(headers, 'api_key') == (False, 'Missing signature header')


def test_verify_headers_valid(setup):
    """Test that valid API key and signature headers pass verification."""
    headers = {
        request_validator.API_KEY_HEADER_NAME: 'api_key',
        request_validator.SIGNATURE_HEADER_NAME: 'signature',
    }
    assert request_validator.verify_headers(headers, 'api_key') == (True, "")


def test_verify_headers_invalid_api_key(setup):
    """Test that an invalid API key fails verification."""
    headers = {request_validator.API_KEY_HEADER_NAME: 'invalid_api_key'}
    assert request_validator.verify_headers(headers, 'api_key') == (False, 'Invalid API key')


def test_verify_get_headers_for_missing_auth(setup):
    """Test that valid headers pass verification."""
    headers = {
        request_validator.CONSUMER_KEY_NAME: 'some-key'
    }
    assert request_validator.verify_headers_for_consumers(
        headers) == (False, "Missing Authorization header")


def test_verify_headers_for_consumers_missing_consumer(setup):
    """Test that valid headers pass verification."""
    headers = {
        "Authorization": 'auth',
    }
    assert request_validator.verify_headers_for_consumers(
        headers) == (False, "Missing Consumer key header")


def test_verify_headers_for_consumers_valid(setup):
    """Test that valid headers pass verification."""
    headers = {
        "Authorization": 'auth',
        request_validator.CONSUMER_KEY_NAME: 'some-key'
    }
    assert request_validator.verify_headers_for_consumers(
        headers) == (True, "")


def test_verify_consumer_not_found(setup):
    """Test that a Consumer is found with given consumer_key"""
    returned_consumer, error_message = request_validator.verify_consumer("not-a-consumer")
    assert returned_consumer == None
    assert error_message == "Consumer not valid"


def test_verify_consumer_no_key(setup):
    """Test that a Consumer is found with given consumer_key"""
    returned_consumer, error_message = request_validator.verify_consumer(None)
    assert returned_consumer == None
    assert error_message == "Consumer not valid"


def test_verify_consumer_found(setup, consumer):
    """Test that a Consumer is found with given consumer_key"""
    returned_consumer, _ = request_validator.verify_consumer("some-consumer")
    assert returned_consumer.id == consumer.id
