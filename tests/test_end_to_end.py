import azure.storage.blob
import dotenv
import logging
import os
import pytest
import subprocess
import time

"""
End to end test for the azure functions using docker compose.
To run the test with logging output use the following command:

pytest --log-cli-level=INFO tests/test_end_to_end.py
"""

ENV_FILE = os.getenv("ENV_FILE", ".env.e2e")


@pytest.fixture()
def setup():
    if not os.getenv("GITHUB_ACTIONS"):
        pytest.skip("Skipping end to end test, set GITHUB_ACTIONS env var to run this test")

    dotenv.load_dotenv(dotenv_path=ENV_FILE)


@pytest.fixture
def docker():
    try:
        assert docker_compose_build(), "Error building containers"
        assert docker_compose_up()
        yield
    finally:
        docker_compose_down()


def docker_arglist(command, *args):
    return ['docker', 'compose', '--env-file', ENV_FILE, '--profile', 'test', command, *args]


def docker_compose_build():
    logging.info("Building containers")
    try:
        subprocess.run(
            docker_arglist('build', 'azurite', 'azurite-setup', 'notify', 'process-pilot-data'),
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        return True
    except Exception as e:
        logging.error(f"Error building containers: {e.stderr}")
        return False


def docker_compose_up():
    logging.info("Starting containers")
    try:
        subprocess.Popen(
            docker_arglist('up', '-d'),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        return True
    except Exception as e:
        logging.error(f"Error building containers: {e.stderr}")
        return False


def docker_compose_down():
    logging.info("Stopping containers")
    subprocess.run(
        docker_arglist('down'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


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


def logs_for_container(container_name):
    result = subprocess.run(
        docker_arglist('logs', container_name, '--since', '30s'),
        check=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    logging.debug(f"Logs for {container_name}: {result.stdout}")

    return result.stdout


def logs_contain_message(container_name, message):
    container_logs = logs_for_container(container_name)
    return message in container_logs


def poll_logs_for_message(container_name, message, cycles=20):
    for _ in range(cycles):
        time.sleep(2)
        if logs_contain_message(container_name, message):
            return True

    return False


def test_end_to_end(setup, docker):
    assert poll_logs_for_message("azurite-setup", "Blob containers created"), (
        "Containers not ready")

    logging.info("Containers are ready")

    assert upload_file_to_blob_storage(), "File upload unsuccessful"

    assert poll_logs_for_message("process-pilot-data", "Trigger Details:"), (
            "ProcessPilotData function not triggered by file upload")

    assert logs_contain_message(
            "process-pilot-data", "Executing 'Functions.ProcessPilotData'"), (
            "ProcessPilotData function not executed")
    assert logs_contain_message(
            "notify", "Executing 'Functions.Notify'"), (
            "Notify function not executed")
    assert poll_logs_for_message(
            "process-pilot-data", "Executed 'Functions.ProcessPilotData' (Succeeded,"), (
            "ProcessPilotData function did not succeed")
    assert poll_logs_for_message(
            "notify", "Executed 'Functions.Notify' (Succeeded,"), (
            "Notify function did not succeed")

    logging.info("End to end test successful")
