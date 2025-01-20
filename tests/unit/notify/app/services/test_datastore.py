import app.services.datastore as datastore
import app.utils.database as database
from datetime import datetime, timedelta
import json
import pytest


@pytest.fixture
def batch_message_data() -> dict[str, str | dict]:
    return {
        "batch_id": "499c8396-16a0-417c-849e-f0062940cd2a",
        "details": json.dumps({"test": "details"}),
        "message_reference": "ee43e0ae-c2ca-4c44-8ddb-266c6dfd3b5e",
        "nhs_number": "1234567890",
        "recipient_id": "a1a77bf2-d5e2-430b-85ea-ac0ba8a59132",
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


def test_create_batch_message_record(batch_message_data):
    """Test the SQL execution of batch message record creation."""
    datastore.create_batch_message_record(batch_message_data)

    with database.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM batch_messages WHERE batch_id = %s",
                (batch_message_data["batch_id"],)
            )
            row = cur.fetchone()

            assert row[0] == batch_message_data["batch_id"]
            assert row[1] - datetime.now() < timedelta(seconds=1)
            assert row[2:7] == (
                json.loads(batch_message_data["details"]),
                batch_message_data["message_reference"],
                batch_message_data["nhs_number"],
                batch_message_data["recipient_id"],
                batch_message_data["status"]
            )


def test_create_batch_message_record_error(batch_message_data):
    """Test the error handling of batch message record creation."""
    batch_message_data["batch_id"] = "invalid"

    assert not datastore.create_batch_message_record(batch_message_data)


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
