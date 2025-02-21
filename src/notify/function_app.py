import azure.functions as func
from app import create_app
import app.services.message_batch_dispatcher as message_batch_dispatcher
import dotenv
import file_processor.csv_file_processor as csv_file_processor
import logging
import os

funcapp = func.FunctionApp()
flaskapp = create_app()

if "ENV_FILE" in os.environ:
    dotenv.load_dotenv(os.environ["ENV_FILE"])

BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME", "file-upload-data")


@funcapp.function_name(name="NotifyApi")
@funcapp.route(
    route="{*route}",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.GET, func.HttpMethod.POST],
)
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(flaskapp.wsgi_app).handle(req, context)


@funcapp.function_name(name="ProcessFileUpload")
@funcapp.blob_trigger(
    arg_name="csvblob",
    path="%BLOB_CONTAINER_NAME%/{name}.csv",
    connection="AzureWebJobsStorage",
)
def process_file_upload(csvblob: func.InputStream):
    logging.info(f"Processing uploaded file: {csvblob.name}")
    raw_data = csvblob.read().decode("utf-8").splitlines()
    filename = os.path.splitext(os.path.basename(csvblob.name))[0]
    message_batch_body = csv_file_processor.message_batch_body(filename, raw_data)
    status_code, response = message_batch_dispatcher.dispatch(message_batch_body)
    logging.info(
        f"Response from Notify API: {status_code}"
        f"\n{response}"
    )
