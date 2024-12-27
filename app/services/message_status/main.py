import json
import logging
from app.services.message_status import status_recorder, request_verifier
from flask import jsonify

def create_message_status(req_body, headers):
    logging.info("MessageStatus HTTP trigger function. Processing callback from NHS Notify service.")
    logging.debug(req_body)

    if not request_verifier.verify_headers(headers):
        status_code = 401
        body = {"status": "error"}
    elif request_verifier.verify_signature(headers, req_body):
        body_dict = json.loads(req_body)
        status_recorder.save_statuses(body_dict)
        status_code = 200
        body = {"status": "success"}
    else:
        status_code = 403
        body = {"status": "error"}

    return body, status_code

def health_check():
    return jsonify({"status": "healthy"}), 200
