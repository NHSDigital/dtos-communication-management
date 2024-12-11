import uuid_generator


def test_reference_uuid():
    """Tests the predictable conversion of a value to a UUID."""
    val = "test"
    assert uuid_generator.reference_uuid(val) == "098f6bcd-4621-d373-cade-4e832627b4f6"


def test_recipient_id():
    """Tests the predictable conversion of a dict containing nhs_number and date_of_birth to a UUID."""
    message_data = {
        "appointment_date": "2025-02-01",
        "appointment_time": "12:00",
        "date_of_birth": "1970-01-01",
        "nhs_number": "1234567890",
    }
    assert uuid_generator.recipient_id(message_data) == "43b1d23b-42b5-9700-e677-1159c15d378f"
