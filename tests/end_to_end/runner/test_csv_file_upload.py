import azure.storage.blob
import app.utils.database as database
import app.models as models
import app.utils.hmac_signature as hmac_signature
import dotenv
import logging
import os
import time
from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session

ENV_FILE = os.getenv("ENV_FILE", ".env.compose")
dotenv.load_dotenv(dotenv_path=ENV_FILE)


def csv_data():
    return (
        'UNUSED_STAGE_COLUMN,9990548609,987654,"BLAKE, KYLIE, MRS",07M09M1971,EP700,01M12M2024,10:15:00,'
        '"The Royal Shrewsbury Hospital, Breast Screening Office, Treatment Centre, Mytton Oak Road, Shrewsbury, SY3 8XQ"'
        "\n"
        'UNUSED_STAGE_COLUMN,9435732992,987654,"BLAKE, KAREN, MRS",04M02M1980,EP700,03M01M2025,11:25:00,'
        '"The Epping Breast Screening Unit, St Margaret\'s Hospital, The Plain, Epping, Essex, CM16 6TN"'
        "\n"
    )


def upload_file_to_blob_storage():
    logging.info("Uploading file to blob storage")
    try:
        azurite_connection_string = os.getenv('AZURITE_CONNECTION_STRING')
        blob_container_name = os.getenv('BLOB_CONTAINER_NAME')
        blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string(azurite_connection_string)
        pilot_data_client = blob_service_client.get_container_client(blob_container_name)
        blob_client = pilot_data_client.get_blob_client("HWA NHS App Pilot 002 SPRPT.csv")
        content_settings = azure.storage.blob.ContentSettings(content_type='text/csv')
        blob_client.upload_blob(csv_data(), blob_type="BlockBlob", content_settings=content_settings, overwrite=True)
    except Exception as e:
        logging.error("Error uploading file to blob storage:")
        logging.error(e)
        return False

    return True


def test_csv_file_upload():
    assert upload_file_to_blob_storage()


def test_csv_file_upload_saves_to_database():
    assert upload_file_to_blob_storage()

    # Wait for the function app to be triggered, make a request to NHS Notify Stub and save the data to the database
    time.sleep(2)

    with Session(database.engine()) as session:
        message_batch = session.scalars(select(models.MessageBatch)).all()[0]
        messages = session.scalars(select(models.Message)).all()

        assert message_batch.id == messages[0].batch_id
        assert message_batch.status == models.MessageBatchStatuses.SENT

        assert len(messages) == 2
        assert messages[0].batch_id == message_batch.id
