import app.models as models
import app.utils.database as database
import app.utils.hmac_signature as hmac_signature
import dotenv
from .helpers import get_status_endpoint, upload_file_to_blob_storage
from pytest_steps import test_steps
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session
import time
import pytest


pytestmark = pytest.mark.test_id(["DTOSS-4691#1.1", "DTOSS-4691#2.1", "DTOSS-4691#1.3"])

dotenv.load_dotenv()


@test_steps(
    'upload_file_to_blob_storage',
    'check_records_saved_to_database',
    'check_get_statuses_endpoint'
)
def test_file_upload_end_to_end():
    assert upload_file_to_blob_storage()

    yield

    # Wait for the function app to be triggered, make a request to NHS Notify Stub and save the data to the database
    time.sleep(5)

    with Session(database.engine()) as session:
        message_batch = session.scalars(select(models.MessageBatch)).all()[0]
        messages = session.scalars(select(models.Message)).all()

        assert message_batch.id == messages[0].batch_id
        assert message_batch.status == models.MessageBatchStatuses.SENT

        assert len(messages) == 2
        assert messages[0].batch_id == message_batch.id

    yield

    response = get_status_endpoint(message_batch.batch_reference)

    assert response.status_code == 200

    json_data = response.json()
    supplier_statuses = [status["supplierStatus"] for status in json_data["data"]]
    assert json_data["status"] == "success"
    assert len(json_data["data"]) == 6
    assert ["notified", "read", "received"] == sorted(list(set(supplier_statuses)))

    yield
