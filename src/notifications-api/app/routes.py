from flask import Blueprint, jsonify

api = Blueprint("api", __name__)


@api.route("/status/health-check", methods=["GET"])
def status_health_check():
    return jsonify({"status": "healthy"}), 200
