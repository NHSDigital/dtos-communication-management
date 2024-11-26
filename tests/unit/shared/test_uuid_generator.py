import uuid_generator


def test_reference_uuid():
    """Tests the predictable conversion of a value to a UUID."""
    val = "test"
    assert uuid_generator.reference_uuid(val) == "098f6bcd-4621-d373-cade-4e832627b4f6"


def test_message_reference():
    """Tests the predictable conversion of some message data stored in a dict to a UUID."""
    message_data = {
        "nhs_number": "1234567890",
        "date_of_birth": "01/01/1970",
        "appointment_date": "01/01/2021",
        "appointment_time": "12:00",
    }
    assert uuid_generator.message_reference(message_data) == "65ee3cb2-35b1-a9df-0a7a-574300738e0e"


def test_recipient_id():
    """Tests the predictable conversion of a dict containing nhs_number and date_of_birth to a UUID."""
    message_data = {
        "nhs_number": "1234567890",
        "date_of_birth": "01/01/1970",
    }
    assert uuid_generator.recipient_id(message_data) == "b2e5a632-111c-a342-7246-42482f9cab5c"
