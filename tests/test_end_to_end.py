import asyncio
import logging
import subprocess

"""
End to end test for the azure functions using docker compose.
To run the test with logging output use the following command:

pytest --log-cli-level=INFO tests/test_end_to_end.py
"""


def run_docker_compose():
    try:

        result = subprocess.Popen(
            ['docker', 'compose', '-f', 'compose.yml', '--env-file', '.env.local', 'up'],
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
        result = subprocess.run(
            ['python', 'dependencies/azurite/send_file.py', 'dependencies/azurite/example.csv'],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )

    except subprocess.CalledProcessError as e:
        logging.error("Error uploading file:")
        logging.error(e)

    return result.stdout, result.stderr


def stop_containers():
    try:
        subprocess.Popen(
            ['docker', 'compose', '-f', 'compose.yml', '--env-file', '.env.local', 'down'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    except Exception as e:
        logging.error("Error stopping containers:")
        logging.error(e)


async def main():
    logging.info("Starting containers")
    output, errors = run_docker_compose()
    logging.info("Pausing for 20 seconds to allow containers to start")
    await asyncio.sleep(20)
    logging.info("Uploading file to blob storage")
    upload_file_to_blob_storage()
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


def test_end_to_end():
    asyncio.run(main())
