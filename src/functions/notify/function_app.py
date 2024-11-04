import azure.functions as func
import json
import helper

app = func.FunctionApp()


@app.function_name(name="Notify")
@app.route(route="notify/{notification_type}/send", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    notification_type: str = req.route_params.get("notification_type")
    req_body_bytes: bytes = req.get_body()
    json_body: str = json.loads(req_body_bytes.decode("utf-8"))

    if notification_type == "message":
        return helper.send_messages(json_body)
