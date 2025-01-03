import hashlib
import hmac
import request_verifier
import pytest


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('NOTIFY_API_KEY', 'api_key')


def test_verify_signature_invalid(setup):
    """Test that an invalid signature fails verification."""
    headers = {request_verifier.SIGNATURE_HEADER_NAME: 'signature'}
    body = 'body'

    assert not request_verifier.verify_signature(headers, body)


def test_verify_signature_valid(setup):
    """Test that a valid signature passes verification."""
    body = 'body'
    signature = hmac.new(
        bytes('application_id.api_key', 'ASCII'),
        msg=bytes(body, 'ASCII'),
        digestmod=hashlib.sha256
    ).hexdigest()

    headers = {request_verifier.SIGNATURE_HEADER_NAME: signature}
    assert request_verifier.verify_signature(headers, body)


def test_verify_headers_missing_all(setup):
    """Test that missing all headers fails verification."""
    headers = {}
    assert not request_verifier.verify_headers(headers)


def test_verify_headers_missing_api_key(setup):
    """Test that missing API key header fails verification."""
    headers = {request_verifier.SIGNATURE_HEADER_NAME: 'signature'}
    assert not request_verifier.verify_headers(headers)


def test_verify_headers_missing_signature(setup):
    """Test that missing signature header fails verification."""
    headers = {request_verifier.API_KEY_HEADER_NAME: 'api_key'}
    assert not request_verifier.verify_headers(headers)


def test_verify_headers_valid(setup):
    """Test that valid API key and signature headers pass verification."""
    headers = {
        request_verifier.API_KEY_HEADER_NAME: 'api_key',
        request_verifier.SIGNATURE_HEADER_NAME: 'signature',
    }
    assert request_verifier.verify_headers(headers)


def test_verify_headers_invalid_api_key(setup):
    """Test that an invalid API key fails verification."""
    headers = {request_verifier.API_KEY_HEADER_NAME: 'invalid_api_key'}
    assert not request_verifier.verify_headers(headers)
