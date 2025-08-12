import app.models as models
import app.services.message_batch_recorder as message_batch_recorder
import app.utils.access_token as access_token
import logging
import os
import requests
import uuid


def dispatch(body: dict, consumer_id: int, bearer_token: str | None = None) -> tuple[int, str]:
    if not bearer_token:
        bearer_token = access_token.get_token()

    response = requests.post(url(), json=body, headers=headers(bearer_token), timeout=10)
    print('–––––––––––––– here is notify response')
    print(response.json())
    logging.info("Response from Notify API %s: %s", url(), response.status_code)

    success = response.status_code == 201
    status = models.MessageBatchStatuses.SENT if success else models.MessageBatchStatuses.FAILED
    message_batch_recorder.save_batch(body, response.json(), status, consumer_id)

    return response.status_code, response.json()


def headers(bearer_token) -> dict:
    return {
        "content-type": "application/vnd.api+json",
        "accept": "*/*",
        "x-correlation-id": str(uuid.uuid4()),
        "authorization": "Bearer " + bearer_token,
        "prefer": "code=401"
    }


def url() -> str:
    return f"{os.getenv('NOTIFY_API_URL')}/comms/v1/message-batches"
