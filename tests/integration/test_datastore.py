import datastore
import dotenv
import json
import logging
import pytest
import uuid

dotenv.load_dotenv(".env.test")


@pytest.fixture(autouse=True, scope="function")
def truncate_table():
    with datastore.connection().cursor() as cur:
        cur.execute("TRUNCATE TABLE batch_messages")
        cur.execute("TRUNCATE TABLE message_statuses")
    datastore.connection().commit()


def batch_message_data(merge_data={}):
    original_data = {
        "batch_id": str(uuid.uuid4()),
        "message_reference": str(uuid.uuid4()),
        "nhs_number": "1234567890",
        "details": json.dumps({"test": "data"}),
        "recipient_id": str(uuid.uuid4()),
        "status": "not_sent",
    }
    return original_data | merge_data


def message_status_data(merge_data={}):
    original_data = {
        "idempotency_key": str(uuid.uuid4()),
        "message_id": str(uuid.uuid4()),
        "message_reference": str(uuid.uuid4()),
        "details": json.dumps({"test": "data"}),
        "status": "created",
    }
    return original_data | merge_data


def test_create_batch_message_record():
    data = batch_message_data()

    actual = datastore.create_batch_message_record(data)
    assert (data["batch_id"], data["message_reference"]) == actual


def test_create_batch_message_record_with_duplicate_primary_key():
    data = batch_message_data()
    datastore.create_batch_message_record(data)

    assert datastore.create_batch_message_record(data) is False


def test_create_batch_message_record_with_invalid_status():
    data = batch_message_data({"status": "invalid"})
    datastore.create_batch_message_record(data)

    assert datastore.create_batch_message_record(data) is False


def test_create_batch_message_record_with_invalid_details():
    data = batch_message_data({"details": "invalid"})
    datastore.create_batch_message_record(data)

    assert datastore.create_batch_message_record(data) is False


def test_create_batch_message_record_with_malicious_values():
    data = batch_message_data({"nhs_number": "DROP TABLE batch_messages;"})
    datastore.create_batch_message_record(data)

    assert datastore.create_batch_message_record(data) is False


def test_create_message_status_record_idempotency_key_exists():
    duplicate_key = str(uuid.uuid4())
    data = message_status_data({"idempotency_key": duplicate_key})
    datastore.create_message_status_record(message_status_data({"idempotency_key": duplicate_key}))

    assert datastore.create_message_status_record(data) is False


def test_create_message_status_record():
    data = message_status_data()

    assert datastore.create_message_status_record(data) == data["idempotency_key"]


def test_create_message_status_record_with_invalid_status():
    data = message_status_data({"status": "invalid"})
    datastore.create_message_status_record(data)

    assert datastore.create_message_status_record(data) is False


def test_create_message_status_record_with_invalid_details():
    data = message_status_data({"details": "invalid"})
    datastore.create_message_status_record(data)

    assert datastore.create_message_status_record(data) is False


def test_create_message_status_record_with_malicious_values():
    data = message_status_data({"nhs_number": "DROP TABLE message_statuses;"})
    datastore.create_message_status_record(data)

    assert datastore.create_message_status_record(data) is False
