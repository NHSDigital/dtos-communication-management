import logging
import pytest
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


@pytest.fixture
def docker():
    try:
        assert docker_compose_build(), "Error building containers"
        assert docker_compose_up()
        yield
    finally:
        docker_compose_down()


def docker_arglist(command, *args):
    return ['docker', 'compose', '--env-file', ENV_FILE, command, *args]


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
        subprocess.run(
            ['python', 'dependencies/azurite/send_file.py', 'dependencies/azurite/example.csv'],
            check=True,
            env=dict(os.environ, ENV_FILE=ENV_FILE),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        logging.info("File uploaded successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error uploading file to blob storage: {e.stderr}")
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


def poll_logs_for_message(container_name, message, cycles=15):
    for _ in range(cycles):
        time.sleep(2)
        if logs_contain_message(container_name, message):
            return True

    return False


def test_end_to_end(skip_test, docker):
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
