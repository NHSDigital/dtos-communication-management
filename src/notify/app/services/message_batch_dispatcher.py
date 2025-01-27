import app.services.message_batch_recorder as message_batch_recorder
import app.utils.access_token as access_token
import database.models as models
import logging
import os
import requests
import uuid


def dispatch(body: dict) -> tuple[int, str]:
    response = requests.post(url(), json=body, headers=headers())
    logging.info(f"Response from Notify API {url()}: {response.status_code}")

    success = response.status_code == 201
    status = models.MessageBatchStatuses.SENT if success else models.MessageBatchStatuses.FAILED
    message_batch_recorder.save_batch(body, response.json(), status)

    return response.status_code, response.json()


def headers() -> dict:
    return {
        "content-type": "application/vnd.api+json",
        "accept": "application/vnd.api+json",
        "x-correlation-id": str(uuid.uuid4()),
        "authorization": "Bearer " + access_token.get_token(),
    }


def url() -> str:
    return f"{os.getenv('NOTIFY_API_URL')}/comms/v1/message-batches"
