import pytest
import uuid
import json
from app.utils.datastore import create_batch_message_record, create_status_record, connection


def batch_message_data(merge_data={}):
    """Generate batch message data with optional overrides."""
    original_data = {
        "batch_id": str(uuid.uuid4()),
        "message_reference": str(uuid.uuid4()),
        "nhs_number": "1234567890",
        "details": json.dumps({"test": "data"}),
        "recipient_id": str(uuid.uuid4()),
        "status": "not_sent",
    }
    return original_data | merge_data


def status_data(merge_data={}):
    """Generate status record data with optional overrides."""
    original_data = {
        "idempotency_key": str(uuid.uuid4()),
        "message_id": str(uuid.uuid4()),
        "message_reference": str(uuid.uuid4()),
        "details": json.dumps({"test": "data"}),
        "status": "created",
    }
    return original_data | merge_data


# def test_create_batch_message_record():
#     """Test successful creation of a batch message record."""
#     data = batch_message_data()

#     actual = create_batch_message_record(data)
#     assert (data["batch_id"], data["message_reference"]) == actual

#     with connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute("SELECT batch_id, details, message_reference, nhs_number, status FROM batch_messages")
#             record = cur.fetchone()

#             assert record == (
#                 data["batch_id"],
#                 {"test": "data"},
#                 data["message_reference"],
#                 data["nhs_number"],
#                 data["status"],
#             )


def test_create_batch_message_record_with_duplicate_primary_key():
    """Test failure when trying to create a record with a duplicate primary key."""
    data = batch_message_data()
    create_batch_message_record(data)

    assert create_batch_message_record(data) is False


def test_create_batch_message_record_with_invalid_status():
    """Test failure when creating a record with an invalid status."""
    data = batch_message_data({"status": "invalid"})
    assert create_batch_message_record(data) is False


def test_create_batch_message_record_with_invalid_details():
    """Test failure when creating a record with invalid details."""
    data = batch_message_data({"details": "invalid"})
    assert create_batch_message_record(data) is False


def test_create_batch_message_record_with_malicious_values():
    """Test failure when malicious values are provided in batch message data."""
    data = batch_message_data({"nhs_number": "DROP TABLE batch_messages;"})
    assert create_batch_message_record(data) is False


# def test_create_status_record():
#     """Test successful creation of a status record."""
#     data = status_data()

#     assert create_status_record(data) == data["idempotency_key"]


def test_create_status_record_with_duplicate_idempotency_key():
    """Test failure when trying to create a status record with a duplicate idempotency key."""
    duplicate_key = str(uuid.uuid4())
    data = status_data({"idempotency_key": duplicate_key})
    create_status_record(data)

    assert create_status_record(data) is False


def test_create_status_record_with_invalid_status():
    """Test failure when creating a status record with an invalid status."""
    data = status_data({"status": "invalid"})
    assert create_status_record(data) is False


def test_create_status_record_with_invalid_details():
    """Test failure when creating a status record with invalid details."""
    data = status_data({"details": "invalid"})
    assert create_status_record(data) is False


def test_create_status_record_with_malicious_values():
    """Test failure when malicious values are provided in status data."""
    data = status_data({"details": "DROP TABLE message_statuses;"})
    assert create_status_record(data) is False


# def test_create_channel_status_record():
#     """Test successful creation of a channel status record."""
#     data = status_data({"status": "read"})

#     assert create_status_record(data, is_channel_status=True) == data["idempotency_key"]


def test_create_channel_status_record_with_invalid_status():
    """Test failure when creating a channel status record with an invalid status."""
    data = status_data({"status": "invalid"})

    assert create_status_record(data, is_channel_status=True) is False
