from flask import Blueprint, jsonify
from flask import request
import json
import app.lib.request_verifier as request_verifier


api = Blueprint("api", __name__)


@api.route("/status/health-check", methods=["GET"])
def status_health_check():
    return jsonify({"status": "healthy"}), 200


@api.route("/status/create", methods=["POST"])
def create_status():
    if request_verifier.verify_headers(dict(request.headers)) is False:
        status_code = 401
        body = {"status": "error"}
    elif request_verifier.verify_signature(dict(request.headers), json.dumps(request.form)):
        # status_recorder.save_statuses(body_dict)
        status_code = 200
        body = {"status": "success"}
    else:
        status_code = 403
        body = {"status": "error"}

    return body, status_code
