import azure.storage.blob
import dotenv
import glob
import logging
import os
import pytest
import time

ENV_FILE = os.getenv("ENV_FILE", ".env.test")


@pytest.fixture()
def setup():
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
            "9990548609,1971-09-07,2024-12-01,10:15,London E5,Mammogram",
            "9435732992,1980-02-04,2025-01-03,11:25,London E1,Mammogram"
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


def poll_logs_for_message(container_name, message, cycles=20):
    for _ in range(cycles):
        time.sleep(2)
        if logs_contain_message(container_name, message):
            return True

    return False


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

    logging.info("End to end test successful")
