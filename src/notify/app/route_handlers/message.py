from flask import request
import app.validators.request_validator as request_validator
import app.services.message_batch_dispatcher as message_batch_dispatcher
import os


def batch():
    json_data = request.json or {}
    valid_headers, error_message = request_validator.verify_headers(
        dict(request.headers), client_api_key()
    )

    if not valid_headers:
        return {"status": "failed", "error": error_message}, 401

    if not request_validator.verify_signature(dict(request.headers), json_data, signature_secret()):
        return {"status": "failed", "error": "Invalid signature"}, 403

    valid_body, error_message = request_validator.verify_body(json_data)

    if not valid_body:
        return {"status": "failed", "error": error_message}, 422

    status_code, response = message_batch_dispatcher.dispatch(json_data)
    status = "success" if status_code == 201 else "failed"

    return {"status": status, "response": response}, status_code


# TODO: This will need to vary per client
def client_api_key() -> str:
    return str(os.getenv("CLIENT_API_KEY"))


# TODO: This will need to vary per client
def signature_secret() -> str:
    return f"{os.getenv('CLIENT_APPLICATION_ID')}.{os.getenv('CLIENT_API_KEY')}"
