import app.models as models
import app.services.message_batch_recorder as message_batch_recorder
import app.services.status_recorder as status_recorder
import app.services.status_reporter as status_reporter
import app.utils.database as database
import copy
import datetime
from hashlib import sha256
import uuid
from sqlalchemy.orm import Session

def test_statuses_for_supplier_status_are_found(channel_status_post_body, consumer, message_batch):
    """Test searching channel status records by supplier status"""

    status_recorder.save_statuses(channel_status_post_body)

    another_nhsapp_channel_status = channel_status_post_body.copy()
    another_nhsapp_channel_status["data"][0]["attributes"]["supplierStatus"] = "notified"
    another_nhsapp_channel_status["data"][0]["meta"]["idempotencyKey"] = sha256(b"another_idempotency_key").hexdigest()
    status_recorder.save_statuses(another_nhsapp_channel_status)

    query_params = {"channel": "nhsapp", "supplierStatus": "read"}

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    attrs = statuses[0].details["data"][0]["attributes"]

    assert len(statuses) == 1
    assert attrs["channel"] == "nhsapp"
    assert attrs["supplierStatus"] == "read"


def test_statuses_for_channel_status_are_found(channel_status_post_body, consumer, message_batch):
    """Test searching channel status records by channel status"""
    status_recorder.save_statuses(channel_status_post_body)

    another_nhsapp_channel_status = channel_status_post_body.copy()
    another_nhsapp_channel_status["data"][0]["attributes"]["channelStatus"] = "received"
    another_nhsapp_channel_status["data"][0]["meta"]["idempotencyKey"] = sha256(b"another_idempotency_key").hexdigest()
    status_recorder.save_statuses(another_nhsapp_channel_status)

    query_params = {"channel": "nhsapp", "channelStatus": "received"}

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    attrs = statuses[0].details["data"][0]["attributes"]

    assert len(statuses) == 1
    assert attrs["channel"] == "nhsapp"
    assert attrs["channelStatus"] == "received"


def test_statuses_for_channel_are_found(channel_status_post_body, consumer, message_batch):
    """Test searching channel status records by channel"""
    status_recorder.save_statuses(channel_status_post_body)

    another_nhsapp_channel_status = channel_status_post_body.copy()
    another_nhsapp_channel_status["data"][0]["attributes"]["channel"] = "sms"
    another_nhsapp_channel_status["data"][0]["meta"]["idempotencyKey"] = sha256(b"another_idempotency_key").hexdigest()
    status_recorder.save_statuses(another_nhsapp_channel_status)

    query_params = {"channel": "sms"}

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    attrs = statuses[0].details["data"][0]["attributes"]

    assert len(statuses) == 1
    assert attrs["channel"] == "sms"


def test_statuses_for_created_after_are_found(channel_status_post_body, consumer, message_batch):
    """Test searching channel status records created after a certain time"""
    status_recorder.save_statuses(channel_status_post_body)

    query_params = {"createdAfter": "2025-01-01T00:00:00Z"}

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    assert len(statuses) == 1


def test_statuses_for_created_before_are_found(channel_status_post_body, consumer, message_batch):
    """Test searching channel status records created before a certain time"""
    status_recorder.save_statuses(channel_status_post_body)

    query_params = {"createdBefore": f"{datetime.datetime.now().year + 1}-01-01T00:00:00Z"}

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    assert len(statuses) == 1


def test_statuses_for_multiple_criteria_are_found(channel_status_post_body, consumer, message_batch):
    """Test searching channel status records by multiple criteria"""
    status_recorder.save_statuses(channel_status_post_body)

    query_params = {"channel": "nhsapp", "channelStatus": "delivered", "supplierStatus": "read", "createdAfter": "2025-01-01T00:00:00Z"}

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    attrs = statuses[0].details["data"][0]["attributes"]

    assert len(statuses) == 1
    assert attrs["channel"] == "nhsapp"
    assert attrs["channelStatus"] == "delivered"
    assert attrs["supplierStatus"] == "read"


def test_statuses_for_nhs_number_are_found(channel_status_post_body, message_batch_post_body, message_batch_post_response, consumer):
    """Test searching channel status records by NHS number"""
    message_batch_recorder.save_batch(message_batch_post_body, message_batch_post_response, models.MessageBatchStatuses.SENT, consumer.id)
    status_recorder.save_statuses(channel_status_post_body)

    query_params = {"nhsNumber": "4010232137"}

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    assert len(statuses) == 1


def test_statuses_for_batch_reference_are_found(message_batch_post_body, message_batch_post_response, channel_status_post_body, consumer):
    """Test searching channel status records by batch reference"""
    message_batch_recorder.save_batch(message_batch_post_body, message_batch_post_response, models.MessageBatchStatuses.SENT, consumer.id)
    status_recorder.save_statuses(channel_status_post_body)

    another_message_batch_reference = str(uuid.uuid4())
    another_message_batch_post_body = message_batch_post_body.copy()
    another_message_batch_post_body["data"]["attributes"]["messageBatchReference"] = another_message_batch_reference
    another_message_batch_post_response = message_batch_post_response.copy()
    another_message_batch_post_response["data"]["attributes"]["messages"][0]["id"] = "another_message_id"
    another_message_batch_post_response["data"]["attributes"]["messageBatchReference"] = another_message_batch_reference
    message_batch_recorder.save_batch(another_message_batch_post_body, another_message_batch_post_response, models.MessageBatchStatuses.SENT, consumer.id)

    another_channel_status_post_body = channel_status_post_body.copy()
    another_channel_status_post_body["data"][0]["attributes"]["messageId"] = another_message_batch_post_response["data"]["attributes"]["messages"][0]["id"]
    another_channel_status_post_body["data"][0]["meta"]["idempotencyKey"] = sha256(b"another_idempotency_key").hexdigest()
    status_recorder.save_statuses(another_channel_status_post_body)

    query_params = {
        "batchReference": message_batch_post_response["data"]["attributes"]["messageBatchReference"],
        "channel": "nhsapp",
        "channelStatus": "delivered",
        "supplierStatus": "read",
        "createdAfter": "2025-01-01T00:00:00Z",
    }

    statuses = status_reporter.get_statuses(query_params, consumer.id)
    assert len(statuses) == 1
    assert statuses[0].details == channel_status_post_body


def test_statuses_are_filtered_by_consumer(channel_status_post_body, consumer, message_batch_post_body, message_batch_post_response, message_batch):
    """Test only statuses for the specified consumer are returned"""
    status_recorder.save_statuses(channel_status_post_body)

    # create message batches and statuses for another consumer, that should not be returned
    with Session(database.engine()) as session:
        another_consumer = session.query(models.Consumer).filter_by(key="some-other-consumer").one_or_none()
        if not another_consumer:
            another_consumer = models.Consumer(key="some-other-consumer")
            session.add(another_consumer)
        session.commit()

        another_message_batch_reference = str(uuid.uuid4())
        another_message_batch_post_body = message_batch_post_body.copy()
        another_message_batch_post_body["data"]["attributes"]["messageBatchReference"] = another_message_batch_reference
        another_message_batch_post_response = message_batch_post_response.copy()
        another_message_batch_post_response["data"]["attributes"]["messages"][0]["id"] = "another_message_id"
        another_message_batch_post_response["data"]["attributes"]["messageBatchReference"] = another_message_batch_reference
        message_batch_recorder.save_batch(
            another_message_batch_post_body,
            another_message_batch_post_response,
            models.MessageBatchStatuses.SENT,
            another_consumer.id
        )

        another_channel_status_post_body = copy.deepcopy(channel_status_post_body)
        another_channel_status_post_body["data"][0]["attributes"]["messageId"] = another_message_batch_post_response["data"]["attributes"]["messages"][0]["id"]
        another_channel_status_post_body["data"][0]["meta"]["idempotencyKey"] = sha256(b"another_idempotency_key").hexdigest()
        status_recorder.save_statuses(another_channel_status_post_body)

    other_statuses = status_reporter.get_statuses({}, another_consumer.id)
    assert len(other_statuses) == 1
    assert other_statuses[0].details == another_channel_status_post_body

    statuses = status_reporter.get_statuses({}, consumer.id)
    assert len(statuses) == 1
    assert statuses[0].details == channel_status_post_body
