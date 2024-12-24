import json
import uuid

SUCCESS_MESSAGE = "Validation successful"
FIELDS = {
    "details": "json",
    "idempotency_key": str,
    "message_reference": uuid.UUID,
    "status": str,
}


def validate(status_params: dict) -> tuple[bool, str]:
    for field, expected_type in FIELDS.items():
        if field not in status_params:
            return False, missing_field_message(field)
        if not validator_for_type(expected_type)(status_params[field]):
            return False, invalid_type_message(field, expected_type)

    return True, SUCCESS_MESSAGE


def validator_for_type(type) -> callable:
    if type == str:
        return valid_string
    if type == uuid.UUID:
        return valid_uuid
    if type == "json":
        return valid_json
    return lambda: False


def valid_string(value):
    return isinstance(value, str)


def valid_uuid(value):
    try:
        return uuid.UUID(value)
    except ValueError:
        return False


def valid_json(value):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return False


def invalid_type_message(field, expected_type):
    return f"Invalid type for field {field}. Expected {expected_type}"


def missing_field_message(field):
    return f"Missing required field: {field}"
