import logging
import os
import requests
from batch_notify.message_batch_body import message_batch_body


ROUTING_PLANS = {
    # FIXME: This is a sandbox routing plan id, not a real one.
    "breast-screening-pilot": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
}
HEADERS = {
    "Content-type": "application/json",
    "Accept": "application/json",
}


def send_message_batch(message_batch_data):
    routing_plan = message_batch_data["routing_plan"]
    data = message_batch_data["data"]
    routing_plan_id = ROUTING_PLANS[routing_plan]

    body = message_batch_body(routing_plan_id, data)
    response = requests.post(url(), json=body, headers=HEADERS)

    if response:
        logging.info(response.text)
    else:
        logging.error(f"{response.status_code} response from Notify API {url()}")
        logging.error(response.text)

    return response.text


def url():
    return base_url() + "/comms/v1/message-batches"


def base_url():
    return os.environ['BASE_URL']
