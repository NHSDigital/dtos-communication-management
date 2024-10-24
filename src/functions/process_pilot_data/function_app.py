import azure.functions as func
import logging
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import helper

BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "pilot-data")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="ProcessPilotData")
@app.blob_trigger(
    arg_name="csvblob", path="%BLOB_CONTAINER_NAME%/{name}.csv", connection="AzureWebJobsStorage"
)
def process_pilot_data(csvblob: func.InputStream) -> str:
    logging.info("Triggering data processor from blob update")
    raw_data = csvblob.read().decode("utf-8").splitlines()
    result = helper.process_data(raw_data)
    logging.info(f"Data processor result: {result}")
