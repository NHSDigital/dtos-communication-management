import azure.functions as func
import json
import logging

app = func.FunctionApp()


@app.function_name(name="StatusCallback")
@app.route(route="status/callback", auth_level=func.AuthLevel.ANONYMOUS)
def main(req: func.HttpRequest) -> func.HttpResponse:
    req_body_bytes: bytes = req.get_body()
    json_body: str = json.loads(req_body_bytes.decode("utf-8"))

    logging.info(json_body)

    return func.HttpResponse(
        body=json.dumps({"status": "success"}).encode("utf-8"),
        status_code=200
    )
