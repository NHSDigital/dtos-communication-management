from app.validators.request_validator import API_KEY_HEADER_NAME, CONSUMER_KEY_NAME
import dotenv
import os
import requests

dotenv.load_dotenv()


def get_status_endpoint(batch_reference):
    headers = {
        "Authorization": "Bearer client_token",
        "Content-Type": "application/json",
        "x-api-key": os.getenv('CLIENT_API_KEY'),
        "x-hmac-sha256-signature": "anything",
        CONSUMER_KEY_NAME: "some-consumer",
    }

    return requests.get(
        f"{os.getenv('NOTIFY_FUNCTION_BASE_URL')}/statuses?batchReference={batch_reference}",
        headers=headers
    )


def post_message_batch_endpoint(message_batch_post_body):
    headers = {
        "Authorization": "Bearer client_token",
        "Content-Type": "application/json",
        CONSUMER_KEY_NAME: "some-consumer",
        API_KEY_HEADER_NAME: os.getenv('CLIENT_API_KEY'),
    }

    return requests.post(
        os.getenv('NOTIFY_FUNCTION_URL'),
        headers=headers,
        json=message_batch_post_body
    )
