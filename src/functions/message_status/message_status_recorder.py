import datastore
import json
import logging
import message_status_validator


def save_message_statuses(request_body: dict) -> None:
    message_statuses: list[dict] = message_status_params(request_body)

    for message_status in message_statuses:
        valid, message = message_status_validator.validate(message_status)
        if valid:
            datastore.create_message_status_record(message_status)
        else:
            logging.error(f"Validation failed: {message}")

    return None


def message_status_params(request_body: dict) -> list[dict]:
    params = []
    for status_data in request_body["data"]:
        try:
            attributes = status_data["attributes"]
            meta = status_data["meta"]
            params.append({
                "details": json.dumps(request_body),
                "idempotency_key": meta["idempotencyKey"],
                "message_id": attributes["messageId"],
                "message_reference": attributes["messageReference"],
                "status": attributes["messageStatus"],
            })
        except KeyError as e:
            logging.error(f"Missing required field: {e}")
            logging.error(f"Request body: {request_body}")
            continue

    return params
