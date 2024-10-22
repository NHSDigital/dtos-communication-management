import azure.functions as func
import logging
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from process_pilot_data.helper import process_data

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="ProcessPilotData")
@app.blob_trigger(arg_name="csvblob", path="blobs/{name}.csv", connection="AzureWebJobsStorage")
def process_pilot_data(csvblob: func.InputStream) -> str:
    logging.info("Triggering data processor from blob update")
    raw_data = csvblob.read().decode("utf-8").splitlines()
    result = process_data(raw_data)
    logging.info(f"Data processor result: {result}")
