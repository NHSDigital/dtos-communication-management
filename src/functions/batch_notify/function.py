import json
import logging

import MessageBatch

import azure.functions as func

app = func.FunctionApp()


@app.function_name(name="BatchMessageBreastScreeningPilot")
@app.route(route="batch-message/breast-screening-pilot", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    req_body_bytes = req.get_body()
    json_body = json.loads(req_body_bytes.decode("utf-8"))
    logging.info(f"JSON body: {json_body}")

    return MessageBatch.call(json_body)
