import azure.functions as func
import json
import logging
import notifier

app = func.FunctionApp()


@app.function_name(name="Notify")
@app.route(
    route="notify/message/send",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.POST],
)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Notify HTTP trigger function. Processing batch notification.")
    req_body_bytes: bytes = req.get_body()
    json_body: str = json.loads(req_body_bytes.decode("utf-8"))

    return notifier.send_messages(json_body)
