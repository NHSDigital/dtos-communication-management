from flask import Blueprint, jsonify

import app.route_handlers.status


api = Blueprint("api", __name__)


@api.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


@api.route("/status/create", methods=["POST"])
def create_status():
    return app.route_handlers.status.create()
