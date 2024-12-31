from flask import Blueprint, request, jsonify
import app.services.status.main as status

api = Blueprint("api", __name__)


# TODO DTOSS-6531 - Rename to /status/create
@api.route("/message-status/create", methods=["POST"])
def create_status():
    data = request.json
    result = status.create_status(data)
    return jsonify(result)

@api.route("/message-status/health-check", methods=["GET"])
def status_health_check():
    result = status.health_check()
    return result
