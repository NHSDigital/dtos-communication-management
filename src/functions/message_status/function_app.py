import azure.functions as func
import json
import logging
import message_status_recorder
import request_verifier

app = func.FunctionApp()


@app.function_name(name="MessageStatus")
@app.route(
    route="message-status/create",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.POST],
)
def main(req: func.HttpRequest) -> func.HttpResponse:
    req_body: str = req.get_body().decode("utf-8")

    logging.info(req_body)

    if request_verifier.verify_headers(req.headers) is False:
        status_code = 401
        body = {"status": "error"}
    elif request_verifier.verify_signature(req.headers, req_body):
        body_dict = json.loads(req_body)
        message_status_recorder.save_message_statuses(body_dict)
        status_code = 200
        body = {"status": "success"}
    else:
        status_code = 403
        body = {"status": "error"}

    return func.HttpResponse(
        status_code=status_code,
        body=json.dumps(body).encode("utf-8")
    )
