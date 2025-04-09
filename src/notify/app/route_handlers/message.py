from flask import request
import app.validators.request_validator as request_validator
import app.services.message_batch_dispatcher as message_batch_dispatcher


def batch():
    if not request.headers.get("Authorization"):
        return {"status": "failed", "error": "Authorization header not present"}, 401

    json_data = request.json or {}

    valid_body, error_message = request_validator.verify_body(json_data)

    if not valid_body:
        return {"status": "failed", "error": error_message}, 422

    status_code, response = message_batch_dispatcher.dispatch(json_data, bearer_token())
    status = "success" if status_code == 201 else "failed"

    return {"status": status, "response": response}, status_code


def bearer_token() -> str:
    header_value = request.headers.get("Authorization")
    if header_value and header_value.startswith("Bearer "):
        return header_value.split(" ")[1]
    return "invalid"
