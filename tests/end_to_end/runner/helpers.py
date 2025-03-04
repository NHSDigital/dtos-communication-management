import app.utils.hmac_signature as hmac_signature
import azure.storage.blob
import dotenv
import json
import logging
import os
import requests

dotenv.load_dotenv()


def signature(body):
    return hmac_signature.create_digest(
        f"{os.getenv('CLIENT_APPLICATION_ID')}.{os.getenv('CLIENT_API_KEY')}",
        json.dumps(body, sort_keys=True)
    )


def get_status_endpoint(batch_reference):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv('CLIENT_API_KEY'),
        "x-hmac-sha256-signature": "anything",
    }

    return requests.get(
        f"{os.getenv('NOTIFY_FUNCTION_BASE_URL')}/statuses?batchReference={batch_reference}",
        headers=headers
    )


def post_message_batch_endpoint(message_batch_post_body):
    hmac_signature = signature(message_batch_post_body)

    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv('CLIENT_API_KEY'),
        "x-hmac-sha256-signature": hmac_signature,
    }

    return requests.post(
        os.getenv('NOTIFY_FUNCTION_URL'),
        headers=headers,
        json=message_batch_post_body
    )


def csv_data():
    return (
        'UNUSED_STAGE_COLUMN,9990548609,987654,"BLAKE, KYLIE, MRS",07M09M1971,EP700,01M12M2024,10:15:00,'
        '"The Royal Shrewsbury Hospital, Breast Screening Office, Treatment Centre, Mytton Oak Road, Shrewsbury, SY3 8XQ"'
        "\n"
        'UNUSED_STAGE_COLUMN,9435732992,987654,"BLAKE, KAREN, MRS",04M02M1980,EP700,03M01M2025,11:25:00,'
        '"The Epping Breast Screening Unit, St Margaret\'s Hospital, The Plain, Epping, Essex, CM16 6TN"'
        "\n"
    )


def upload_file_to_blob_storage():
    logging.info("Uploading file to blob storage")
    try:
        azurite_connection_string = os.getenv('AZURITE_CONNECTION_STRING')
        blob_container_name = os.getenv('BLOB_CONTAINER_NAME')
        blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string(azurite_connection_string)
        pilot_data_client = blob_service_client.get_container_client(blob_container_name)
        blob_client = pilot_data_client.get_blob_client("HWA NHS App Pilot 002 SPRPT.csv")
        content_settings = azure.storage.blob.ContentSettings(content_type='text/csv')
        blob_client.upload_blob(csv_data(), blob_type="BlockBlob", content_settings=content_settings, overwrite=True)
    except Exception as e:
        logging.error("Error uploading file to blob storage:")
        logging.error(e)
        return False

    return True
