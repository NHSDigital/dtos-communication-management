import app.services.message_batch_recorder as message_batch_recorder
import app.utils.database as database
import database.models as models
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session


def test_save_batch(message_batch_post_body, message_batch_post_response):
    """When save_batch is called with a valid batch, the batch and messages should be saved."""
    success, response = message_batch_recorder.save_batch(
        message_batch_post_body["data"],
        message_batch_post_response,
        models.MessageBatchStatuses.SENT
    )
    assert success
    assert response == "Batch id: 1 saved successfully"

    with Session(database.engine()) as session:
        message_batch = session.scalars(select(models.MessageBatch)).all()[0]
        messages = session.scalars(select(models.Message)).all()

        assert message_batch.id == messages[0].batch_id
        assert message_batch.batch_id == message_batch_post_response["data"]["id"]
        assert str(message_batch.batch_reference) == message_batch_post_response["data"]["attributes"]["messageBatchReference"]
        assert message_batch.details == message_batch_post_body["data"]
        assert message_batch.response == message_batch_post_response
        assert message_batch.status == models.MessageBatchStatuses.SENT

        assert len(messages) == 1
        assert messages[0].batch_id == message_batch.id
        assert messages[0].message_id == message_batch_post_response["data"]["attributes"]["messages"][0]["id"]
        assert str(messages[0].message_reference) == message_batch_post_response["data"]["attributes"]["messages"][0]["messageReference"]
        merged_messages = message_batch_recorder.merged_messages(message_batch_post_body["data"], message_batch_post_response)
        assert messages[0].details == merged_messages[0]
        assert messages[0].nhs_number == merged_messages[0]["recipient"]["nhsNumber"]


def test_save_batch_with_failed_status(message_batch_post_body, message_batch_post_response):
    """When save_batch is called with a failed status, the batch should still be saved without message records."""
    success, response = message_batch_recorder.save_batch(
        message_batch_post_body["data"],
        message_batch_post_response,
        models.MessageBatchStatuses.FAILED
    )
    assert success
    assert response == "Batch id: 1 saved successfully"

    with Session(database.engine()) as session:
        message_batch = session.scalars(select(models.MessageBatch)).all()[0]

        assert len(session.scalars(select(models.Message)).all()) == 0
        assert message_batch.batch_id == message_batch_post_response["data"]["id"]
        assert str(message_batch.batch_reference) == message_batch_post_response["data"]["attributes"]["messageBatchReference"]
        assert message_batch.details == message_batch_post_body["data"]
        assert message_batch.response == message_batch_post_response
        assert message_batch.status == models.MessageBatchStatuses.FAILED


def test_save_batch_with_errors(message_batch_post_body, message_batch_post_response):
    """When save_batch fails with an error, the batch should not be saved."""
    success, response = message_batch_recorder.save_batch(
        message_batch_post_body["data"],
        message_batch_post_response,
        "invalid"
    )
    assert not success
    assert 'invalid input value for enum messagebatchstatuses: "invalid"' in response

    with Session(database.engine()) as session:
        assert len(session.scalars(select(models.MessageBatch)).all()) == 0
        assert len(session.scalars(select(models.Message)).all()) == 0
