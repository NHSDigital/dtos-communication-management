import app.services.datastore as datastore
import app.utils.database as database
from datetime import datetime, timedelta
import json
import pytest


@pytest.fixture
def message_batch_data() -> dict[str, str | dict]:
    return {
        "batch_id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
        "batch_reference": "499c8396-16a0-417c-849e-f0062940cd2a",
        "details": json.dumps({"test": "details"}),
        "response": json.dumps({"test": "response"}),
        "status": "sent",
    }


@pytest.fixture
def message_status_data() -> dict[str, str | dict]:
    return {
        "details": json.dumps({"test": "details"}),
        "idempotency_key": "47652cc9-8f76-423b-9923-273af024d264", #gitleaks:allow
        "message_id": "0x0x0x0xabx0x0",
        "message_reference": "5bd25347-f941-461f-952f-773540ad86c9",
        "status": "delivered",
    }


def test_create_message_batch_record(message_batch_data):
    """Test the SQL execution of message batch record creation."""
    datastore.create_message_batch_record(message_batch_data)

    with database.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM message_batches WHERE batch_id = %s",
                (message_batch_data["batch_id"],)
            )
            row = cur.fetchone()

            assert row[1] == message_batch_data["batch_id"]
            assert row[2] == message_batch_data["batch_reference"]
            assert row[3] - datetime.now() < timedelta(seconds=1)
            assert row[4] == json.loads(message_batch_data["details"])
            assert row[5] == json.loads(message_batch_data["response"])
            assert row[6] == message_batch_data["status"]


def test_create_message_batch_record_error(message_batch_data):
    """Test the error handling of message batch record creation."""
    message_batch_data["batch_reference"] = "invalid"

    assert not datastore.create_message_batch_record(message_batch_data)


def test_create_message_status_record(message_status_data):
    """Test the SQL execution of message status record creation."""
    datastore.create_status_record("MessageStatus", message_status_data)

    with database.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM message_statuses WHERE idempotency_key = %s",
                (message_status_data["idempotency_key"],)
            )
            row = cur.fetchone()
            assert row[0] - datetime.now() < timedelta(seconds=1)
            assert row[1:6] == (
                json.loads(message_status_data["details"]),
                message_status_data["idempotency_key"],
                message_status_data["message_id"],
                message_status_data["message_reference"],
                message_status_data["status"]
            )


def test_create_message_status_record_error(message_status_data):
    """Test the error handling of message status record creation."""
    message_status_data["status"] = "invalid"

    assert not datastore.create_status_record("MessageStatus", message_status_data)


def test_create_channel_status_record(message_status_data):
    """Test the SQL execution of channel status record creation."""
    datastore.create_status_record("ChannelStatus", message_status_data)
    channel_status_data = message_status_data

    with database.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM channel_statuses WHERE idempotency_key = %s",
                (channel_status_data["idempotency_key"],)
            )
            row = cur.fetchone()
            assert row[0] - datetime.now() < timedelta(seconds=1)
            assert row[1:6] == (
                json.loads(message_status_data["details"]),
                channel_status_data["idempotency_key"],
                channel_status_data["message_id"],
                channel_status_data["message_reference"],
                channel_status_data["status"]
            )


def test_create_channel_status_record_error(message_status_data):
    """Test the error handling of channel status record creation."""
    message_status_data["status"] = "invalid"

    assert not datastore.create_status_record("ChannelStatus", message_status_data)
