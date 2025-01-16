import app.services.datastore as datastore
import json
import logging


def save_statuses(request_body: dict) -> None:
    statuses: list[dict] = status_params(request_body)
    status_type = request_body["data"][0]["type"]

    for status in statuses:
        datastore.create_status_record(status_type, status)

    return None


def status_params(request_body: dict) -> list[dict]:
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
                "status": attributes.get("messageStatus", attributes.get("channelStatus")),
            })
        except KeyError as e:
            logging.error(f"Missing required field: {e}")
            logging.error(f"Request body: {request_body}")
            continue

    return params
