import app.models as models
import app.utils.database as database
import app.services.status_recorder as status_recorder
import json
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session
import pytest


pytestmark = pytest.mark.test_id(["DTOSS-4691#2.1"])

def test_save_statuses_with_channel_status_data(channel_status_post_body):
    """Test saving channel status data to database"""
    assert status_recorder.save_statuses(channel_status_post_body)
    channel_status_data = channel_status_post_body["data"][0]

    with Session(database.engine()) as session:
        status_record = session.scalars(select(models.ChannelStatus)).all()[0]
        assert status_record.details == channel_status_post_body
        assert status_record.idempotency_key == channel_status_data["meta"]["idempotencyKey"]
        assert status_record.message_id == channel_status_data["attributes"]["messageId"]
        assert str(status_record.message_reference) == channel_status_data["attributes"]["messageReference"]
        assert status_record.status == models.ChannelStatuses(channel_status_data["attributes"]["supplierStatus"])


def test_save_statuses_with_message_status_data(message_status_post_body):
    """Test saving message status data to datastore"""
    assert status_recorder.save_statuses(message_status_post_body)
    message_status_data = message_status_post_body["data"][0]

    with Session(database.engine()) as session:
        status_record = session.scalars(select(models.MessageStatus)).all()[0]
        assert status_record.details == message_status_post_body
        assert status_record.idempotency_key == message_status_data["meta"]["idempotencyKey"]
        assert status_record.message_id == message_status_data["attributes"]["messageId"]
        assert str(status_record.message_reference) == message_status_data["attributes"]["messageReference"]
        assert status_record.status == models.MessageStatuses(message_status_data["attributes"]["messageStatus"])


def test_save_statuses_with_error(mocker, channel_status_post_body):
    """Test saving status data to database with error"""
    mocker.patch("app.services.status_recorder.Session", side_effect=Exception)
    assert not status_recorder.save_statuses(channel_status_post_body)
