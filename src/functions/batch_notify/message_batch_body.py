import hashlib
import time
import uuid

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
