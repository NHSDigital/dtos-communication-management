import json
import logging


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
