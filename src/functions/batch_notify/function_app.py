import json
import logging
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from batch_notify.helper import send_message_batch

import azure.functions as func

app = func.FunctionApp()


@app.function_name(name="BatchNotify")
@app.route(route="batch-notify/breast-screening-pilot", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest):
    req_body_bytes = req.get_body()
    json_body = json.loads(req_body_bytes.decode("utf-8"))
    logging.info(f"JSON body: {json_body}")

    return send_message_batch(json_body)
