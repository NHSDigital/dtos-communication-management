import pytest
import uuid
import validate_message_status

def generate_uuid():
    return str(uuid.uuid4())

@pytest.mark.parametrize(
    "req, expected_result, expected_message",
    [
        # All required fields present/valid
        (
            {
                "batch_id": generate_uuid(),
                "message_reference": generate_uuid(),
                "nhs_number": "1234567890",
                "recipient_id": "recipient123",
            },
            True,
            validate_message_status.success_message,
        ),
        # Missing required field (batch_id)
        (
            {
                "message_reference": generate_uuid(),
                "nhs_number": "1234567890",
                "recipient_id": "recipient123",
            },
            False,
            validate_message_status.missing_field_message("batch_id"),
        ),
        # Invalid type for `batch_id`
        (
            {
                "batch_id": "invalid-uuid",
                "message_reference": generate_uuid(),
                "nhs_number": "1234567890",
                "recipient_id": "recipient123",
            },
            False,
            validate_message_status.invalid_type_message("batch_id", uuid.UUID),
        ),
        # Invalid type for `nhs_number`
        (
            {
                "batch_id": generate_uuid(),
                "message_reference": generate_uuid(),
                "nhs_number": 1234567890,
                "recipient_id": "recipient123",
            },
            False,
            validate_message_status.invalid_type_message("nhs_number", str),
        ),
        #  All optional fields are valid
        (
            {
                "batch_id": generate_uuid(),
                "message_reference": generate_uuid(),
                "nhs_number": "1234567890",
                "recipient_id": "recipient123",
                "current_state": "SENT",
                "message_id": "msg123",
                "full_payload_details": {"key": "value"},
            },
            True,
            validate_message_status.success_message,
        ),
        # Invalid optional field type (current_state)
        (
            {
                "batch_id": generate_uuid(),
                "message_reference": generate_uuid(),
                "nhs_number": "1234567890",
                "recipient_id": "recipient123",
                "current_state": 123,
            },
            False,
            validate_message_status.invalid_type_message("current_state", str),
        ),
    ],
)
def test_validate_message_status(req, expected_result, expected_message):
    result, message = validate_message_status.validate_message_status(req)
    assert result == expected_result
    assert message == expected_message
