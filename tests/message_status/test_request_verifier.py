import hashlib
import hmac
import request_verifier
import pytest


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('OAUTH2_API_KEY', 'api_key')


def test_verify_signature(setup):
    headers = {request_verifier.SIGNATURE_HEADER_NAME: 'signature'}

    assert not request_verifier.verify_signature(headers, 'body')

    signature = hmac.new(
        bytes('application_id.api_key', 'utf-8'),
        msg=bytes('body', 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    headers[request_verifier.SIGNATURE_HEADER_NAME] = signature

    assert request_verifier.verify_signature(headers, 'body')


def test_verify_headers_missing_headers(setup):
    assert not request_verifier.verify_headers({})


def test_verify_headers_missing_api_key_header(setup):
    headers = {request_verifier.SIGNATURE_HEADER_NAME: 'signature'}

    assert not request_verifier.verify_headers(headers)


def test_verify_headers_missing_signature_header(setup):
    headers = {request_verifier.API_KEY_HEADER_NAME: 'api_key'}

    assert not request_verifier.verify_headers(headers)


def test_verify_headers_valid_api_key(setup):
    headers = {
        request_verifier.API_KEY_HEADER_NAME: 'api_key',
        request_verifier.SIGNATURE_HEADER_NAME: 'signature',
    }

    assert request_verifier.verify_headers(headers)


def test_verify_headers_invalid_api_key(setup):
    headers = {request_verifier.API_KEY_HEADER_NAME: 'invalid_api_key'}

    assert not request_verifier.verify_headers(headers)
