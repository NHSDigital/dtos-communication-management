from flask import Flask
from app.routes import api
from app.commands.create_consumer import create_consumer


def create_app():
    app = Flask(__name__)

    app.register_blueprint(api, url_prefix="/api")

    app.cli.add_command(create_consumer)

    return app
