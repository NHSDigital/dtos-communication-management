import app.validators.request_validator as request_validator
import app.utils.hmac_signature as hmac_signature
import json
import pytest


@pytest.fixture
def setup(monkeypatch):
    """Set up environment variables for tests."""
    monkeypatch.setenv('APPLICATION_ID', 'application_id')
    monkeypatch.setenv('NOTIFY_API_KEY', 'api_key')


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
    assert request_validator.verify_headers(headers, 'api_key')


def test_verify_headers_invalid_api_key(setup):
    """Test that an invalid API key fails verification."""
    headers = {request_validator.API_KEY_HEADER_NAME: 'invalid_api_key'}
    assert request_validator.verify_headers(headers, 'api_key') == (False, 'Invalid API key')


def test_verify_body_empty_data_list(setup):
    """Test that an empty data list fails verification."""
    body = {"data": []}
    assert request_validator.verify_body(body) == (False, "Empty data list")


def test_verify_body_mixed_types(setup):
    """Test that a list with mixed types fails verification."""
    body = {
        "data": [
            {"type": "MessageBatch", "content": "test"},
            {"type": "Message", "content": "test"}
        ]
    }
    assert request_validator.verify_body(body) == (False, "All items must have the same type")


def test_verify_body_valid_list(setup):
    """Test that a list with same types passes verification."""
    body = {
        "data": [{
            "type": "MessageBatch",
            "attributes": {
                "messageReference": "REF123",
                "routingPlanId": "PLAN123",
                "recipient": {
                    "nhsNumber": "1234567890",
                    "dateOfBirth": "1990-01-01",
                },
                "personalisation": {
                    "appointment_date": "2024-03-20",
                    "appointment_location": "City Hospital",
                    "appointment_time": "14:30",
                    "tracking_id": "1234567890",
                    "contact_telephone_number": "07700900001",
                },
            },
        },{
            "type": "MessageBatch",
            "attributes": {
                "messageReference": "REF234",
                "routingPlanId": "PLAN234",
                "recipient": {
                    "nhsNumber": "1234567891",
                    "dateOfBirth": "1990-01-01",
                },
                "personalisation": {
                    "appointment_date": "2024-03-21",
                    "appointment_location": "City Hospital",
                    "appointment_time": "14:30",
                    "tracking_id": "1234567891",
                    "contact_telephone_number": "07700900001",
                },
            },
        }]
    }

    assert request_validator.verify_body(body)[0] == True


def test_verify_body_missing_type(setup):
    """Test that missing type field fails verification."""
    body = {
        "data": [
            {"content": "test"}
        ]
    }
    assert request_validator.verify_body(body) == (False, "Invalid body: 'type'")
