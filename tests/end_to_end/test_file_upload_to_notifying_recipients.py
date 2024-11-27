import azure.storage.blob
import dotenv
import glob
import logging
import os
import psycopg2
import pytest
import time

ENV_FILE = os.getenv("ENV_FILE", ".env.test")


@pytest.fixture()
def setup(mocker):
    dotenv.load_dotenv(dotenv_path=ENV_FILE)


def upload_file_to_blob_storage():
    logging.info("Uploading file to blob storage")
    try:
        azurite_connection_string = os.getenv('AZURITE_CONNECTION_STRING')
        blob_container_name = os.getenv('BLOB_CONTAINER_NAME')
        blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string(azurite_connection_string)
        pilot_data_client = blob_service_client.get_container_client(blob_container_name)
        blob_client = pilot_data_client.get_blob_client("example.csv")
        csv_data = "\n".join([
            "9990548609,1971-09-07,2024-12-01,10:15,London E5,0123456789",
            "9435732992,1980-02-04,2025-01-03,11:25,London E1,0123456789",
        ]) + "\n"
        content_settings = azure.storage.blob.ContentSettings(content_type='text/csv')
        blob_client.upload_blob(csv_data, blob_type="BlockBlob", content_settings=content_settings, overwrite=True)
    except Exception as e:
        logging.error("Error uploading file to blob storage:")
        logging.error(e)
        return False

    return True


def log_dir_for_container(container_name):
    return f"/tests/end_to_end/log/functions/{container_name}"


def logs_for_container(container_name):
    logs = glob.glob(f"{log_dir_for_container(container_name)}/*.log")

    assert logs, f"No logs found for container {container_name}"

    with open(logs[0]) as f:
        return f.read()


def logs_contain_message(container_name, message):
    container_logs = logs_for_container(container_name)
    return message in container_logs


def poll_logs_for_message(container_name, message, cycles=40):
    for _ in range(cycles):
        time.sleep(2)
        if logs_contain_message(container_name, message):
            return True

    return False


def assert_batch_messages_database_records_created():
    connection = psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        host=os.environ["DATABASE_HOST"],
        password=os.environ["DATABASE_PASSWORD"]
    )
    with connection as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT details, message_reference, nhs_number, status FROM batch_messages ORDER BY created_at")
            records = cur.fetchall()

            assert len(records) == 4

            details, message_reference, nhs_number, status = records[0]

            assert message_reference == "73ffd0b7-2b7e-20b9-a144-dd30c0231e56"
            assert nhs_number == "9990548609"
            assert status == "not_sent"
            assert details["date_of_birth"] == "1971-09-07"
            assert details["appointment_date"] == "2024-12-01"
            assert details["appointment_time"] == "10:15"
            assert details["appointment_location"] == "London E5"
            assert details["contact_telephone_number"] == "0123456789"

            details, message_reference, nhs_number, status = records[1]

            assert message_reference == "73ffd0b7-2b7e-20b9-a144-dd30c0231e56"
            assert nhs_number == "9990548609"
            assert status == "sent"

            details, message_reference, nhs_number, status = records[2]
            assert message_reference == "3b2edf6a-aa27-0029-1b90-e1b9b120a5a8"
            assert nhs_number == "9435732992"
            assert status == "not_sent"
            assert details["date_of_birth"] == "1980-02-04"
            assert details["appointment_date"] == "2025-01-03"
            assert details["appointment_time"] == "11:25"
            assert details["appointment_location"] == "London E1"
            assert details["contact_telephone_number"] == "0123456789"

            details, message_reference, nhs_number, status = records[3]
            assert message_reference == "3b2edf6a-aa27-0029-1b90-e1b9b120a5a8"
            assert nhs_number == "9435732992"
            assert status == "sent"


def test_end_to_end(setup):
    assert upload_file_to_blob_storage(), "File upload unsuccessful"

    assert poll_logs_for_message("process-pilot-data", "Trigger Details:"), (
            "ProcessPilotData function not triggered by file upload")

    assert poll_logs_for_message(
            "process-pilot-data", "Executing 'Functions.ProcessPilotData'"), (
            "ProcessPilotData function not executed")
    assert poll_logs_for_message(
            "notify", "Executing 'Functions.Notify'"), (
            "Notify function not executed")
    assert poll_logs_for_message(
            "process-pilot-data", "Executed 'Functions.ProcessPilotData' (Succeeded,"), (
            "ProcessPilotData function did not succeed")
    assert poll_logs_for_message(
            "notify", "Executed 'Functions.Notify' (Succeeded,"), (
            "Notify function did not succeed")

    assert_batch_messages_database_records_created()

    logging.info("End to end test successful")
