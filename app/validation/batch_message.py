from typing import Dict, Any

def validate_recipient(recipient: Dict[str, Any]) -> None:
    """Validate recipient data structure"""
    required_fields = {"nhsNumber", "dateOfBirth"}
    missing_fields = required_fields - set(recipient.keys())

    if missing_fields:
        raise ValueError(f"Missing required recipient fields: {missing_fields}")

    if not isinstance(recipient["nhsNumber"], str):
        raise ValueError("nhsNumber must be a string")
    if not isinstance(recipient["dateOfBirth"], str):
        raise ValueError("dateOfBirth must be a string")

def validate_personalisation(personalisation: Dict[str, Any]) -> None:
    """Validate personalisation data structure"""
    # All fields are optional, but if present must be strings
    for field, value in personalisation.items():
        if not isinstance(value, str):
            raise ValueError(f"Field '{field}' must be a string")

def validate_attributes(attributes: Dict[str, Any]) -> None:
    """Validate message attributes"""
    required_fields = {"messageReference", "routingPlanId", "recipient", "personalisation"}
    missing_fields = required_fields - set(attributes.keys())

    if missing_fields:
        raise ValueError(f"Missing required attribute fields: {missing_fields}")

    if not isinstance(attributes["messageReference"], str):
        raise ValueError("messageReference must be a string")
    if not isinstance(attributes["routingPlanId"], str):
        raise ValueError("routingPlanId must be a string")

    validate_recipient(attributes["recipient"])
    validate_personalisation(attributes["personalisation"])

def validate_message_data(message_data: Dict[str, Any]) -> None:
    """Validate message data structure"""
    if not isinstance(message_data, dict):
        raise ValueError("Message data must be a dictionary")

    required_fields = {"type", "attributes"}
    missing_fields = required_fields - set(message_data.keys())

    if missing_fields:
        raise ValueError(f"Missing required message fields: {missing_fields}")

    if message_data["type"] != "MessageBatch":
        raise ValueError('type must be "MessageBatch"')

    validate_attributes(message_data["attributes"])

def validate_batch_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates the NHS Notify message request data.
    Args:
        data: Dictionary containing the message request
    Returns:
        Validated dictionary if valid
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValueError("Request must be a dictionary")

    if "data" not in data:
        raise ValueError("Missing required 'data' field")

    validate_message_data(data["data"])

    return data
