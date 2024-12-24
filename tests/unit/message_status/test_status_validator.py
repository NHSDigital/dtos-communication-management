import status_validator
import uuid


def generate_uuid():
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def test_status_validator_all_fields_valid():
    """Test validation with all required fields present and valid."""
    status_params = {
        "details": '{"abc": 123}',
        "idempotency_key": "idempotency123", #gitleaks:allow
        "message_reference": generate_uuid(),
        "status": "sent",
    }
    result, message = status_validator.validate(status_params)

    assert result is True
    assert message == status_validator.SUCCESS_MESSAGE


def test_status_validator_missing_field():
    """Test validation fails when a required field is missing."""
    status_params = {
        "details": '{"abc": 123}',
        "message_reference": generate_uuid(),
        "status": "sent",
    }
    result, message = status_validator.validate(status_params)

    assert result is False
    assert message == status_validator.missing_field_message("idempotency_key")


def test_status_validator_invalid_type():
    """Test validation fails when a field has an invalid uuid type."""
    status_params = {
        "details": '{"abc": 123}',
        "idempotency_key": "idempotency123", #gitleaks:allow
        "message_reference": "message123",
        "status": "sent",
    }
    result, message = status_validator.validate(status_params)

    assert result is False
    assert message == status_validator.invalid_type_message("message_reference", uuid.UUID)


def test_status_validator_invalid_json():
    """Test validation fails when the details field is not valid JSON."""
    status_params = {
        "details": "abc123",
        "idempotency_key": "idempotency123", #gitleaks:allow
        "message_reference": generate_uuid(),
        "status": "sent",
    }
    result, message = status_validator.validate(status_params)

    assert result is False
    assert message == status_validator.invalid_type_message("details", "json")
