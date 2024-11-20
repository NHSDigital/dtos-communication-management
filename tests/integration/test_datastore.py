import datastore
import dotenv
import json
import pytest
import uuid

dotenv.load_dotenv(".env.test")


@pytest.fixture(autouse=True, scope="function")
def truncate_table():
    with datastore.connection().cursor() as cur:
        cur.execute("TRUNCATE TABLE message_statuses")
    datastore.connection().commit()


def message_status_data(merge_data={}):
    original_data = {
        "batch_id": str(uuid.uuid4()),
        "idempotency_key": str(uuid.uuid4()),
        "message_id": str(uuid.uuid4()),
        "message_reference": str(uuid.uuid4()),
        "nhs_number": "1234567890",
        "details": json.dumps({"test": "data"}),
        "recipient_id": str(uuid.uuid4()),
        "state": "created",
    }
    return original_data | merge_data


def test_idempotency_key_exists():
    duplicate_key = str(uuid.uuid4())
    data = message_status_data({"idempotency_key": duplicate_key})
    datastore.create_message_status_record(message_status_data({"idempotency_key": duplicate_key}))

    assert datastore.create_message_status_record(data) is False


def test_message_reference_not_found():
    data = message_status_data({"message_reference": str(uuid.uuid4())})
    data.pop("batch_id")

    assert datastore.create_message_status_record(data) is False


def test_create_message_status_record():
    data = message_status_data()

    assert datastore.create_message_status_record(data) == data["idempotency_key"]


def test_create_message_status_record_without_batch_id():
    data = message_status_data()
    datastore.create_message_status_record(data)

    data["idempotency_key"] = str(uuid.uuid4())
    data.pop("batch_id")

    assert datastore.create_message_status_record(data) == data["idempotency_key"]


def test_create_message_status_record_with_invalid_state():
    data = message_status_data({"state": "invalid"})
    datastore.create_message_status_record(data)

    assert datastore.create_message_status_record(data) is False


def test_create_message_status_record_with_invalid_details():
    data = message_status_data({"details": "invalid"})
    datastore.create_message_status_record(data)

    assert datastore.create_message_status_record(data) is False


def test_create_message_status_record_with_malicious_values():
    data = message_status_data({"recipient_id": "DROP TABLE message_statuses;"})
    datastore.create_message_status_record(data)

    assert datastore.create_message_status_record(data) is False
