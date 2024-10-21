import hashlib
import time
import uuid


class MessageBatchBody:
    @classmethod
    def call(cls, routing_plan_id, enumberable):
        api_messages = [cls.api_message(item) for item in enumberable]
        return cls.api_body(routing_plan_id, api_messages)

    @classmethod
    def api_body(cls, routing_plan_id, api_messages):
        return {
            "data": {
                "type": "MessageBatch",
                "attributes": {
                    "messageBatchReference": cls.reference_uuid(time.time()),
                    "routingPlanId": routing_plan_id,
                    "messages": api_messages,
                },
            }
        }

    @classmethod
    def api_message(cls, message_data):
        return {
            "messageReference": cls.reference_uuid(message_data["nhs_number"]),
            "recipient": {
                "nhsNumber": message_data["nhs_number"],
                "dateOfBirth": message_data["date_of_birth"],
            },
            "personalisation": {},
        }

    @classmethod
    def reference_uuid(cls, val):
        str_val = str(val)
        return str(uuid.UUID(hashlib.md5(str_val.encode()).hexdigest()))
