from flask import Blueprint, request, jsonify
import app.services.message_status.main as message_status

api = Blueprint("api", __name__)

@api.route("/message-status/create", methods=["POST"])
def create_message_status():
    data = request.json
    result = message_status.create_message_status(data)
    return jsonify(result)

@api.route("/message-status/health-check", methods=["GET"])
def message_status_health_check():
    result = message_status.health_check()
    return result
