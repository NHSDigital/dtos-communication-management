import azure.functions as func
from app import create_app
from app.commands.create_consumer import _create_consumer
import dotenv
from migrations.utils import alembic_migrate
import os
import json

funcapp = func.FunctionApp()
flaskapp = create_app()

if "ENV_FILE" in os.environ:
    dotenv.load_dotenv(os.environ["ENV_FILE"])


@funcapp.function_name(name="NotifyApi")
@funcapp.route(
    route="{*route}",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.GET, func.HttpMethod.POST],
)
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(flaskapp.wsgi_app).handle(req, context)

@funcapp.function_name(name="MigrateDatabase")
@funcapp.route(
    route="migrate-database",
    auth_level=func.AuthLevel.FUNCTION,
    methods=[func.HttpMethod.POST],
)
def migrate_database(req: func.HttpRequest) -> func.HttpResponse:
    if req.headers.get("x-migration-key") != os.getenv("DATABASE_PASSWORD"):
        return func.HttpResponse(
            "Unauthorized",
            status_code=401,
        )

    migration_info = alembic_migrate()

    return func.HttpResponse(
        f"Database migration complete: {migration_info}",
        status_code=200,
    )

@funcapp.function_name(name="CreateConsumer")
@funcapp.route(
    route="consumer",
    auth_level=func.AuthLevel.FUNCTION,
    methods=[func.HttpMethod.POST],
)
def create_consumer(req: func.HttpRequest) -> func.HttpResponse:
    key = req.get_json().get("key")
    if key is None:
        return func.HttpResponse(
            "Missing key field",
            status_code=400,
        )

    consumer, message = _create_consumer(key)

    if consumer:
        return func.HttpResponse(
            json.dumps({ 'id': consumer.id, 'key': consumer.key}).encode(),
            status_code=201,
        )

    return func.HttpResponse(
        message,
        status_code=500,
    )
