import azure.functions as func
import azurefunctions.extensions.bindings.blob as blob
import logging

from functions.process_pilot_data.data_processor import DataProcessor

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.blob_trigger(
    arg_name="client", path="dir1/dir2/blob", connection="AzureWebJobsStorage"
)
def blob_trigger(client: blob.BlobClient):
    logging.info("Triggering batch message from blob update")
    DataProcessor.call(client.download_blob.readall())
