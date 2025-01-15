from flask import request
import json
import app.validators.request_validator as request_validator


def create():
    if request_validator.verify_headers(dict(request.headers)) is False:
        status_code = 401
        body = {"status": "error"}
    elif request_validator.verify_signature(dict(request.headers), json.dumps(request.form)) is False:
        status_code = 403
        body = {"status": "error"}
    elif request_validator.verify_body(dict(request.form)) is False:
        status_code = 422
        body = {"status": "error"}
    else:
        # status_recorder.save_statuses(body_dict)
        status_code = 200
        body = {"status": "success"}

    return body, status_code
