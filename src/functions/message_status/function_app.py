import azure.functions as func
import json
import logging
import status_recorder
import request_verifier

app = func.FunctionApp()


@app.function_name(name="MessageStatus")
@app.route(
    route="message-status/create",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.POST],
)
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("MessageStatus HTTP trigger function. Processing callback from NHS Notify service.")
    req_body: str = req.get_body().decode("utf-8")

    logging.debug(req_body)

    if request_verifier.verify_headers(req.headers) is False:
        status_code = 401
        body = {"status": "error"}
    elif request_verifier.verify_signature(req.headers, req_body):
        body_dict = json.loads(req_body)
        status_recorder.save_statuses(body_dict)
        status_code = 200
        body = {"status": "success"}
    else:
        status_code = 403
        body = {"status": "error"}

    return func.HttpResponse(
        status_code=status_code,
        body=json.dumps(body).encode("utf-8")
    )


@app.function_name(name="MessageStatusHealthCheck")
@app.route(
    route="message-status/health-check",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=[func.HttpMethod.GET],
)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        status_code=200,
        body=json.dumps({"status": "healthy"}).encode("utf-8")
    )
