import azure.functions as func
from app import create_app

funcapp = func.FunctionApp()
flaskapp = create_app()


@funcapp.route(
    route="{*route}",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.GET, func.HttpMethod.POST],
)
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(flaskapp.wsgi_app).handle(req, context)
