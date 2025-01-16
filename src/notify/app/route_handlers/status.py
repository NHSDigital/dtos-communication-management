from flask import request
import app.validators.request_validator as request_validator
import app.services.status_recorder as status_recorder


def create():
    if request_validator.verify_headers(dict(request.headers)) is False:
        status_code = 401
        body = {"status": "error"}
    elif request_validator.verify_signature(dict(request.headers), request.json) is False:
        status_code = 403
        body = {"status": "error"}
    elif request_validator.verify_body(request.json)[0] is False:
        status_code = 422
        body = {"status": "error"}
    else:
        status_recorder.save_statuses(request.json)
        status_code = 200
        body = {"status": "success"}

    return body, status_code
