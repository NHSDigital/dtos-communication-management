import pytest
import uuid
import validate_message_status


def generate_uuid():
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def test_validate_message_status_all_fields_valid():
    """Test validation with all required fields present and valid."""
    req = {
        "batch_id": generate_uuid(),
        "message_reference": generate_uuid(),
        "nhs_number": "1234567890",
        "recipient_id": "recipient123",
    }
    result, message = validate_message_status.validate_message_status(req)

    assert result is True
    assert message == validate_message_status.success_message


def test_validate_message_status_missing_field():
    """Test validation fails when a required field is missing."""
    req = {
        "message_reference": generate_uuid(),
        "nhs_number": "1234567890",
        "recipient_id": "recipient123",
    }
    result, message = validate_message_status.validate_message_status(req)

    assert result is False
    assert message == validate_message_status.missing_field_message("batch_id")


def test_validate_message_status_invalid_type_batch_id():
    """Test validation fails for invalid type of `batch_id`."""
    req = {
        "batch_id": "invalid-uuid",
        "message_reference": generate_uuid(),
        "nhs_number": "1234567890",
        "recipient_id": "recipient123",
    }
    result, message = validate_message_status.validate_message_status(req)

    assert result is False
    assert message == validate_message_status.invalid_type_message("batch_id", uuid.UUID)


def test_validate_message_status_invalid_type_nhs_number():
    """Test validation fails for invalid type of `nhs_number`."""
    req = {
        "batch_id": generate_uuid(),
        "message_reference": generate_uuid(),
        "nhs_number": 1234567890,
        "recipient_id": "recipient123",
    }
    result, message = validate_message_status.validate_message_status(req)

    assert result is False
    assert message == validate_message_status.invalid_type_message("nhs_number", str)


def test_validate_message_status_optional_fields_valid():
    """Test validation passes with all optional fields valid."""
    req = {
        "batch_id": generate_uuid(),
        "message_reference": generate_uuid(),
        "nhs_number": "1234567890",
        "recipient_id": "recipient123",
        "current_state": "SENT",
        "message_id": "msg123",
        "full_payload_details": {"key": "value"},
    }
    result, message = validate_message_status.validate_message_status(req)

    assert result is True
    assert message == validate_message_status.success_message


def test_validate_message_status_invalid_optional_field_type():
    """Test validation fails for invalid type of an optional field."""
    req = {
        "batch_id": generate_uuid(),
        "message_reference": generate_uuid(),
        "nhs_number": "1234567890",
        "recipient_id": "recipient123",
        "current_state": 123,
    }
    result, message = validate_message_status.validate_message_status(req)

    assert result is False
    assert message == validate_message_status.invalid_type_message("current_state", str)
