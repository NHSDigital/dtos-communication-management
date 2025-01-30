import azure.functions as func
from app import create_app
import dotenv
import os

funcapp = func.FunctionApp()
flaskapp = create_app()

if "ENV_FILE" in os.environ:
    dotenv.load_dotenv(os.environ["ENV_FILE"])


@funcapp.route(
    route="{*route}",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.GET, func.HttpMethod.POST],
)
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(flaskapp.wsgi_app).handle(req, context)
