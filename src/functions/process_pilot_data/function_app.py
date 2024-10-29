import azure.functions as func
import process_pilot_data.helper
import logging
import os


BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "pilot-data")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="ProcessPilotData")
@app.blob_trigger(
    arg_name="csvblob", path="%BLOB_CONTAINER_NAME%/{name}.csv", connection="AzureWebJobsStorage"
)
def process_data(csvblob: func.InputStream) -> str:
    logging.info("Triggering data processor from blob update")
    raw_data = csvblob.read().decode("utf-8").splitlines()
    result = process_pilot_data.helper.process_data(raw_data)
    logging.info(f"Data processor result: {result}")
