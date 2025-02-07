import pytest
from app.validation.batch_message import validate_batch_message

def test_valid_message():
    valid_request = {
        "data": {
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
                    "contact_telephone_number": "07700900000",
                },
            },
        }
    }
    result = validate_batch_message(valid_request)
    assert result["data"]["type"] == "MessageBatch"
    assert result["data"]["attributes"]["messageReference"] == "REF123"

def test_rejects_missing_required_fields():
    invalid_request = {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "messageReference": "REF123",
                # missing routingPlanId
                "recipient": {
                    "nhsNumber": "1234567890",
                    "dateOfBirth": "1990-01-01",
                },
                "personalisation": {
                    "appointment_date": "2024-03-20",
                    "appointment_location": "City Hospital",
                    "appointment_time": "14:30",
                    "tracking_id": "1234567890",
                    "contact_telephone_number": "07700900000",
                },
            },
        }
    }
    with pytest.raises(ValueError):
        validate_batch_message(invalid_request)

def test_rejects_invalid_message_type():
    invalid_request = {
        "data": {
            "type": "InvalidType",  # should be "MessageBatch"
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
                    "contact_telephone_number": "07700900000",
                },
            },
        }
    }
    with pytest.raises(ValueError, match='type must be "MessageBatch"'):
        validate_batch_message(invalid_request)

def test_rejects_missing_recipient_fields():
    invalid_request = {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "messageReference": "REF123",
                "routingPlanId": "PLAN123",
                "recipient": {
                    # missing nhsNumber
                    "dateOfBirth": "1990-01-01",
                },
                "personalisation": {
                    "appointment_date": "2024-03-20",
                    "appointment_location": "City Hospital",
                    "appointment_time": "14:30",
                    "tracking_id": "1234567890",
                    "contact_telephone_number": "07700900000",
                },
            },
        }
    }
    with pytest.raises(ValueError):
        validate_batch_message(invalid_request)

def test_allows_empty_personalisation():
    valid_request = {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "messageReference": "REF123",
                "routingPlanId": "PLAN123",
                "recipient": {
                    "nhsNumber": "1234567890",
                    "dateOfBirth": "1990-01-01",
                },
                "personalisation": {},  # Empty personalisation is valid
            },
        }
    }
    result = validate_batch_message(valid_request)
    assert result["data"]["attributes"]["personalisation"] == {}

def test_validates_personalisation_field_types():
    invalid_request = {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "messageReference": "REF123",
                "routingPlanId": "PLAN123",
                "recipient": {
                    "nhsNumber": "1234567890",
                    "dateOfBirth": "1990-01-01",
                },
                "personalisation": {
                    "some_field": True  # Should be a string
                },
            },
        }
    }
    with pytest.raises(ValueError, match="Field 'some_field' must be a string"):
        validate_batch_message(invalid_request)
