import app.utils.datastore as datastore
import json
import logging
import app.services.status.status_validator as status_validator


def save_statuses(request_body: dict) -> None:
    for data in request_body["data"]:
        status_data = status_params(data)
        valid, message = status_validator.validate(status_data)
        if valid:
            is_channel_status = "channelStatus" in data["attributes"]
            datastore.create_status_record(status_data, is_channel_status)
        else:
            logging.error(f"Validation failed: {message}")

    return None


def status_params(status_data: dict):
    try:
        attributes = status_data["attributes"]
        meta = status_data["meta"]
        status = attributes.get("channelStatus", attributes.get("messageStatus"))
        return {
            "details": json.dumps(status_data),
            "idempotency_key": meta["idempotencyKey"],
            "message_id": attributes["messageId"],
            "message_reference": attributes["messageReference"],
            "status": status,
        }
    except KeyError as e:
        logging.error(f"Missing key: {e}")
        return None
