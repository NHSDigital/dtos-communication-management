import json
import logging
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import helper

import azure.functions as func

app = func.FunctionApp()


@app.function_name(name="Notify")
@app.route(route="notify/{notification_type}/send", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    notification_type: str = req.route_params.get("notification_type")
    req_body_bytes: bytes = req.get_body()
    json_body: str = json.loads(req_body_bytes.decode("utf-8"))
    logging.info(f"JSON body: {json_body}")

    if notification_type == "message":
        return helper.send_messages(json_body)
