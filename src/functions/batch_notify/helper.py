import hashlib
import logging
import os
import requests
import time
import uuid


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


def message_batch_body(routing_plan_id, enumberable):
    api_messages = [api_message(item) for item in enumberable]
    return api_body(routing_plan_id, api_messages)


def api_body(routing_plan_id, api_messages):
    return {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "messageBatchReference": reference_uuid(time.time()),
                "routingPlanId": routing_plan_id,
                "messages": api_messages,
            },
        }
    }


def api_message(message_data):
    return {
        "messageReference": reference_uuid(message_data["nhs_number"]),
        "recipient": {
            "nhsNumber": message_data["nhs_number"],
            "dateOfBirth": message_data["date_of_birth"],
        },
        "personalisation": {},
    }


def reference_uuid(val):
    str_val = str(val)
    return str(uuid.UUID(hashlib.md5(str_val.encode()).hexdigest()))
