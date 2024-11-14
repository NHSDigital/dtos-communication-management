import azure.functions as func
import json
import logging
import request_verifier

app = func.FunctionApp()


@app.function_name(name="StatusCallback")
@app.route(route="status/callback", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    req_body: str = req.get_body().decode("utf-8")

    logging.info(json.loads(req_body))

    if request_verifier.verify_headers(req.headers) is False:
        status_code = 401
        body = {"status": "error"}
    elif request_verifier.verify_signature(req.headers, req_body):
        status_code = 200
        body = {"status": "success"}
    else:
        status_code = 403
        body = {"status": "error"}

    return func.HttpResponse(
        status_code=status_code,
        body=json.dumps(body).encode("utf-8")
    )
