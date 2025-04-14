import app.models as models
import app.utils.database as database
import app.utils.hmac_signature as hmac_signature
import dotenv
from .helpers import post_message_batch_endpoint, get_status_endpoint
from pytest_steps import test_steps
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session
import time
import pytest

dotenv.load_dotenv()


pytestmark = pytest.mark.test_id(["DTOSS-4691#2.1", "DTOSS-4691#1.3"])

@test_steps(
    'post_to_message_batch_endpoint_saves_to_database',
    'status_create_endpoint_saves_to_database',
    'statuses_endpoint_returns_correct_statuses'
)
def test_post_message_batch_end_to_end(message_batch_post_body, message_batch_post_response):
    response = post_message_batch_endpoint(message_batch_post_body)

    # Wait for the callbacks to be received and saved to the database
    time.sleep(9)

    assert response.status_code == 201

    with Session(database.engine()) as session:
        message_batch = session.scalars(select(models.MessageBatch)).all()[0]
        messages = session.scalars(select(models.Message)).all()

        assert message_batch.id == messages[0].batch_id
        assert message_batch.batch_id == message_batch_post_response["data"]["id"]
        assert str(message_batch.batch_reference) == message_batch_post_response["data"]["attributes"]["messageBatchReference"]
        assert message_batch.details == message_batch_post_body
        assert message_batch.status == models.MessageBatchStatuses.SENT

        assert len(messages) == 1
        assert messages[0].batch_id == message_batch.id
        assert str(messages[0].message_reference) == message_batch_post_response["data"]["attributes"]["messages"][0]["messageReference"]

    yield

    with Session(database.engine()) as session:
        # NHS Notify Stub sends 3 status callbacks for each message
        channel_statuses = session.scalars(
            select(models.ChannelStatus).where(models.ChannelStatus.message_id == messages[0].message_id)
        ).all()

        assert len(channel_statuses) == 3

        for channel_status in channel_statuses:
            assert channel_status.message_id == messages[0].message_id
            assert channel_status.message_reference == messages[0].message_reference

        message_statuses = session.scalars(select(models.MessageStatus)).all()

        assert len(message_statuses) == 1
        assert message_statuses[0].message_id == messages[0].message_id
        assert message_statuses[0].message_reference == messages[0].message_reference

    yield

    response = get_status_endpoint(message_batch.batch_reference)

    assert response.status_code == 200

    json_data = response.json()
    supplier_statuses = [status["supplierStatus"] for status in json_data["data"]]
    assert json_data["status"] == "success"
    assert len(json_data["data"]) == 3
    assert ["notified", "read", "received"] == sorted(supplier_statuses)

    yield
