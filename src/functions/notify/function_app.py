import azure.functions as func
import json
import logging
import notifier

app = func.FunctionApp()


@app.function_name(name="Notify")
@app.route(route="notify/{notification_type}/send", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Notify HTTP trigger function. Processing batch notification.")
    notification_type: str = req.route_params.get("notification_type")
    req_body_bytes: bytes = req.get_body()
    json_body: str = json.loads(req_body_bytes.decode("utf-8"))

    if notification_type == "message":
        return notifier.send_messages(json_body)
