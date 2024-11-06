import asyncio
import azure.storage.blob
import dotenv
import io
import logging
import pytest
import os
import subprocess
import traceback

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


def run_docker_compose_build():
    logging.info("Building containers")
    try:
        subprocess.run(
            ['docker', 'compose', '-f', 'compose.yml', '--env-file', ENV_FILE, 'build'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
    except Exception as e:
        logging.error("Error building containers:")
        logging.error(e)
        return False

    return True


def run_docker_compose_up():
    logging.info("Starting containers")
    try:
        result = subprocess.Popen(
            ['docker', 'compose', '-f', 'compose.yml', '--env-file', ENV_FILE, 'up'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
    except Exception as e:
        logging.error("Error starting containers:")
        logging.error(e)

    return result.stdout, result.stderr


def upload_file_to_blob_storage():
    try:
        azurite_connection_string = os.getenv('AZURITE_CONNECTION_STRING')
        blob_container_name = os.getenv('BLOB_CONTAINER_NAME')
        blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string(azurite_connection_string)
        pilot_data_client = blob_service_client.get_container_client(blob_container_name)
        blob_client = pilot_data_client.get_blob_client("example.csv")
        data = "1234567890,01/01/2000,01/01/2022,09:00,123 Fake Street,First Appointment\n"
        content_settings = azure.storage.blob.ContentSettings(content_type='text/csv')
        blob_client.upload_blob(data, blob_type="BlockBlob", content_settings=content_settings, overwrite=True)
    except Exception as e:
        traceback.print_exc()
        logging.error("Error uploading file to blob storage:")
        logging.error(e)
        return False

    return True


def stop_containers():
    try:
        subprocess.run(
            ['docker', 'compose', '-f', 'compose.yml', '--env-file', ENV_FILE, 'down'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    except Exception as e:
        logging.error("Error stopping containers:")
        logging.error(e)


async def main():
    logging.info("Starting end to end test")
    run_docker_compose_build()
    output, errors = run_docker_compose_up()
    logging.info("Pausing for 30 seconds to allow containers to start")
    await asyncio.sleep(30)
    logging.info("Uploading file to blob storage")
    assert upload_file_to_blob_storage()
    logging.info("Pausing for 5 seconds to allow functions to execute")
    await asyncio.sleep(5)
    logging.info("Stopping containers")
    stop_containers()

    container_output = output.read()

    logging.debug("Container output:")
    logging.debug(container_output)

    assert "Executing 'Functions.ProcessPilotData' (Reason='New blob detected(LogsAndContainerScan): pilot-data/example.csv'" in container_output
    assert "Executed 'Functions.ProcessPilotData' (Succeeded," in container_output

    assert "Executing 'Functions.Notify' (Reason='This function was programmatically called via the host APIs.'" in container_output
    assert "Executed 'Functions.Notify' (Succeeded," in container_output

    logging.info("End to end test completed successfully")


def test_end_to_end(setup):
    asyncio.run(main())
