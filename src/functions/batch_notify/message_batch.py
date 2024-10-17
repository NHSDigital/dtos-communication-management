import logging
import os
import requests
from functions.batch_notify.message_batch_body import MessageBatchBody


class MessageBatch:
    ROUTING_PLANS = {
        # FIXME: This is a sandbox routing plan id, not a real one.
        "breast-screening-pilot": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
    }
    HEADERS = {
        "Content-type": "application/json",
        "Accept": "application/json",
    }

    @classmethod
    def call(cls, message_batch_data):
        routing_plan = message_batch_data["routing_plan"]
        data = message_batch_data["data"]
        routing_plan_id = cls.ROUTING_PLANS[routing_plan]

        body = MessageBatchBody.call(routing_plan_id, data)
        response = requests.post(cls.url(), json=body, headers=cls.HEADERS)

        if response:
            logging.info(response.text)
        else:
            logging.error(f"{response.status_code} response from Notify API {cls.url}\n")
            logging.error(response.text)

        # TODO: Wrap this response for consumers
        return response

    @classmethod
    def url(cls):
        return cls.base_url() + "/comms/v1/message-batches"

    @classmethod
    def base_url(cls):
        return os.environ['BASE_URL']
