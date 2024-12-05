import azure.functions as func
import data_processor
import logging
import os


BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "pilot-data")

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="ProcessPilotData")
@app.blob_trigger(
    arg_name="csvblob",
    path="%BLOB_CONTAINER_NAME%/{name}.csv",
    connection="AzureWebJobsStorage",
)
def process_data(csvblob: func.InputStream) -> str:
    logging.info("ProcessPilotData blob InputStream trigger function. Processing pilot data upload.")
    raw_data = csvblob.read().decode("utf-8").splitlines()
    filename = os.path.splitext(os.path.basename(csvblob.name))[0]
    result = data_processor.process_data(filename, raw_data)
    logging.info(f"Data processor result: {result}")
