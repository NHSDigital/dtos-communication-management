import azure.storage.blob
import dotenv
import logging
import os
import requests

dotenv.load_dotenv()


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
    headers = {
        "Authorization": "Bearer client_token",
        "Content-Type": "application/json",
    }

    return requests.post(
        os.getenv('NOTIFY_FUNCTION_URL'),
        headers=headers,
        json=message_batch_post_body
    )
