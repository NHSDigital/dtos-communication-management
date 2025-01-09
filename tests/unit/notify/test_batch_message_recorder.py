import batch_message_recorder
import datastore
import json
import pytest
import uuid_generator


@pytest.fixture
def batch_message_data():
    return {
        "nhs_number": "1234567890",
        "date_of_birth": "01/01/2000",
        "appointment_date": "01/01/2022",
        "appointment_time": "12:00",
    }


def test_save_status(mocker, batch_message_data):
    """Test saving the status of a batch message."""

    message_reference = "a4629c17-dd22-cef3-a821-32c53effc532"
    mocker.patch("datastore.create_batch_message_record")

    batch_message_recorder.save_status(
        batch_message_recorder.NOT_SENT,
        "some_batch_id",
        message_reference,
        batch_message_data,
    )

    datastore.create_batch_message_record.assert_called_once_with({
        "batch_id": "some_batch_id",
        "details": json.dumps(batch_message_data),
        "message_reference": message_reference,
        "nhs_number": "1234567890",
        "recipient_id": uuid_generator.recipient_id(batch_message_data),
        "status": "not_sent",
    })


def test_save_status_with_specified_details(mocker, batch_message_data):
    """Test saving the status of a batch message with specified details."""

    message_reference = "a4629c17-dd22-cef3-a821-32c53effc532"
    mocker.patch("datastore.create_batch_message_record")
    details = '{"some": "details"}'
    batch_message_data["details"] = details

    batch_message_recorder.save_status(
        batch_message_recorder.SENT,
        "some_batch_id",
        message_reference,
        batch_message_data,
    )

    datastore.create_batch_message_record.assert_called_once_with({
        "batch_id": "some_batch_id",
        "details": details,
        "message_reference": message_reference,
        "nhs_number": "1234567890",
        "recipient_id": uuid_generator.recipient_id(batch_message_data),
        "status": "sent",
    })
