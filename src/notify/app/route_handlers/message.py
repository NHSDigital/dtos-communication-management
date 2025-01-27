from flask import request
import app.validators.request_validator as request_validator
import app.services.message_batch_dispatcher as message_batch_dispatcher


def batch():
    json_data = request.json or {}
    valid_headers, error_message = request_validator.verify_headers(dict(request.headers))

    if not valid_headers:
        return {"status": "failed", "error": error_message}, 401

    if not request_validator.verify_signature(dict(request.headers), json_data):
        return {"status": "failed", "error": "Invalid signature"}, 403

    valid_body, error_message = request_validator.verify_body(json_data)

    if not valid_body:
        return {"status": "failed", "error": error_message}, 422

    status_code, response = message_batch_dispatcher.dispatch(json_data)
    status = "success" if status_code == 201 else "failed"

    return {"status": status, "response": response}, status_code
