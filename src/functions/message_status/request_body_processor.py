import json


def message_status_params(request_body: dict) -> list[dict]:
    params = []
    for status_data in request_body["data"]:
        attributes = status_data["attributes"]
        meta = status_data["meta"]
        params.append({
            "message_id": attributes["messageId"],
            "message_reference": attributes["messageReference"],
            "idempotency_key": meta["idempotencyKey"],
            "status_description": attributes["messageStatusDescription"],
            "status": attributes["messageStatus"],
            "details": json.dumps(request_body),
        })
    return params
