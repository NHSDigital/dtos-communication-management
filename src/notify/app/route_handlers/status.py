from flask import request
import app.validators.request_validator as request_validator
import app.services.status_recorder as status_recorder
import os


def create():
    json_data = request.json or {}
    valid_headers, error_message = request_validator.verify_headers(
        dict(request.headers), str(os.getenv("NOTIFY_API_KEY"))
    )

    if not valid_headers:
        return {"status": error_message}, 401

    if not request_validator.verify_signature(dict(request.headers), json_data, signature_secret()):
        return {"status": "Invalid signature"}, 403

    valid_body, error_message = request_validator.verify_body(json_data)

    if not valid_body:
        return {"status": error_message}, 422

    if status_recorder.save_statuses(json_data):
        return {"status": "success"}, 200


def signature_secret() -> str:
    return f"{os.getenv('APPLICATION_ID')}.{os.getenv('NOTIFY_API_KEY')}"
