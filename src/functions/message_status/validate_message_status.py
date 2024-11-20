import uuid

success_message = "Validation successful"

def invalid_type_message(field, expected_type):
    return f"Invalid type for field {field}. Expected {expected_type.__name__}"

def missing_field_message(field):
    return f"Missing required field: {field}"

def validate_message_status(request):
    required_fields = {
        "batch_id": uuid.UUID,
        "message_reference": uuid.UUID,
        "nhs_number": str,
        "recipient_id": str,
    }

    for field, expected_type in required_fields.items():
        if field not in request:
            return False, missing_field_message(field)
        try:
            if expected_type == uuid.UUID:
                uuid.UUID(request[field])
            elif not isinstance(request[field], expected_type):
                raise ValueError()
        except ValueError:
            return False, invalid_type_message(field, expected_type)

    optional_fields = {
        "current_state": str,
        "message_id": str,
        "full_payload_details": (dict, type(None)),
    }

    for field, expected_type in optional_fields.items():
        if field in request:
            if isinstance(expected_type, tuple):
                if not isinstance(request[field], expected_type):
                    return False, invalid_type_message(field, expected_type)
            elif not isinstance(request[field], expected_type):
                return False, invalid_type_message(field, expected_type)

    return True, success_message
