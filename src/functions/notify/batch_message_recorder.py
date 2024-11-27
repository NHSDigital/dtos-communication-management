import datastore
import json
import logging
import uuid_generator

FAILED = "failed"
NOT_SENT = "not_sent"
SENT = "sent"


def save_status(status: str, batch_id: str, data: dict):
    batch_message_status_data = {
        "batch_id": batch_id,
        "details": data.get("details", json.dumps(data)),
        "message_reference": uuid_generator.message_reference(data),
        "nhs_number": data.get("nhs_number"),
        "recipient_id": uuid_generator.recipient_id(data),
        "status": status,
    }
    logging.info(f"Saving batch message status: {batch_message_status_data}")

    datastore.create_batch_message_record(batch_message_status_data)
