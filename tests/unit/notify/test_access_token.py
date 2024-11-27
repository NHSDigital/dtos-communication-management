import access_token
import logging
import pytest
import requests_mock
import cryptography.hazmat.primitives.asymmetric.rsa as rsa
from cryptography.hazmat.primitives import serialization


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables and private key for tests."""
    monkeypatch.setenv("OAUTH2_TOKEN_URL", "http://tokens.example.com")
    monkeypatch.setenv("OAUTH2_API_KEY", "an_api_key")
    monkeypatch.setenv("OAUTH2_API_KID", "a_kid")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    monkeypatch.setenv("PRIVATE_KEY", private_key_pem)


def test_get_token_successful_response(setup):
    """Test that a valid response returns the expected access token."""
    with requests_mock.Mocker() as mock:
        mock.post(
            "http://tokens.example.com/",
            json={"access_token": "an_access_token"},
        )

        token = access_token.get_token()
        assert token == "an_access_token"


def test_get_token_error_response(setup, mocker):
    """Test that an error response results in an empty token and logs errors."""
    error_logging_spy = mocker.spy(logging, "error")

    with requests_mock.Mocker() as mock:
        mock.post(
            "http://tokens.example.com/",
            status_code=403,
            json={"error": "an_error"},
        )

        token = access_token.get_token()
        assert token == ""
        error_logging_spy.assert_any_call("Failed to get access token")
        error_logging_spy.assert_any_call({"error": "an_error"})
