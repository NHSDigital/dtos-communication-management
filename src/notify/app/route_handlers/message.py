from flask import request
import app.validators.request_validator as request_validator
import app.services.message_batch_dispatcher as message_batch_dispatcher
import os


def batch():
    valid_headers, headers_error_message = request_validator.verify_headers_for_consumers(dict(request.headers), str(os.getenv("CLIENT_API_KEY")))

    if not valid_headers:
        return {"status": "failed", "error": headers_error_message}, 401

    consumer, consumer_error_message = request_validator.verify_consumer(consumer_key())

    if not consumer:
        return {"status": "failed", "error": consumer_error_message}, 401

    json_data = request.json or {}

    valid_body, error_message = request_validator.verify_body(json_data)

    if not valid_body:
        return {"status": "failed", "error": error_message}, 422

    status_code, response = message_batch_dispatcher.dispatch(json_data, consumer.id, bearer_token())
    status = "success" if status_code == 201 else "failed"

    return {"status": status, "response": response}, status_code


def bearer_token() -> str:
    header_value = request.headers.get("Authorization")
    if header_value and header_value.startswith("Bearer "):
        return header_value.split(" ")[1]
    return "invalid"

def consumer_key() -> str | None:
    return request.headers.get(request_validator.CONSUMER_KEY_NAME)
