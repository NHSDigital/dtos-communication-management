import datetime
import hashlib
import jwt
import logging
import os
import requests
import time
import uuid
import routing_plans

def send_messages(data: dict) -> str:
    responses: list = []
    routing_plan_id: str = None

    access_token: str = get_access_token()

    if "routing_plan" in data:
        routing_plan_id = routing_plans.get_id(data.pop("routing_plan"))

    if "recipients" in data:
        for message_data in data["recipients"]:
            if "routing_plan" in message_data:
                routing_plan_id = routing_plans.get_id(message_data.pop("routing_plan"))

            response: str = send_message(access_token, routing_plan_id, message_data)
            responses.append(response)

    return "\n".join(responses)


def send_message(access_token, routing_plan_id, message_data) -> str:
    body: str = message_body(routing_plan_id, message_data)
    correlation_id: str = message_data["correlation_id"]
    response = requests.post(url(), json=body, headers=headers(access_token, correlation_id))

    if response:
        logging.info(response.text)
    else:
        logging.error(f"{response.status_code} response from Notify API {url()}")
        logging.error(response.text)

    return response.text


def headers(access_token: str, correlation_id: str) -> dict:
    return {
        "content-type": "application/vnd.api+json",
        "accept": "application/vnd.api+json",
        "x-correlation-id": correlation_id,
        "authorization": "Bearer " + access_token,
    }


def url() -> str:
    return os.environ["NOTIFY_API_URL"] + "/comms/v1/messages"


def message_body(routing_plan_id, message_data) -> dict:
    nhs_number: str = message_data["nhs_number"]
    date_of_birth: str = message_data["date_of_birth"]
    appointment_time: str = message_data["appointment_time"]
    appointment_date: str = message_data["appointment_date"]
    appointment_location: str = message_data["appointment_location"]
    contact_telephone_number: str = message_data["contact_telephone_number"]

    return {
        "data": {
            "type": "Message",
            "attributes": {
                "messageReference": reference_uuid(nhs_number),
                "routingPlanId": routing_plan_id,
                "recipient": {
                    "nhsNumber": nhs_number,
                    "dateOfBirth": date_of_birth,
                },
                "personalisation": {
                    "appointment_date": appointment_date,
                    "appointment_location": appointment_location,
                    "appointment_time": appointment_time,
                    "tracking_id": nhs_number,
                    "contact_telephone_number": contact_telephone_number,
                },
                "originator": {
                    "odsCode": "X26"
                },
            },
        }
    }


def reference_uuid(val) -> str:
    str_val = str(val)
    return str(uuid.UUID(hashlib.md5(str_val.encode()).hexdigest()))


def get_access_token() -> str:
    if not os.getenv("NOTIFY_API_KEY"):
        return "awaiting-token"

    jwt: str = generate_auth_jwt()
    headers: dict = {"Content-Type": "application/x-www-form-urlencoded"}

    body = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt,
    }

    response = requests.post(os.getenv("OAUTH2_TOKEN_URL"), data=body, headers=headers)
    logging.info(f"Response from OAuth2 token provider: {response.status_code}")
    response_json = response.json()

    if response.status_code == 200:
        access_token = response_json["access_token"]
    else:
        logging.error(f"Failed to get access token: {response_json}")
        access_token = ""

    return access_token


def generate_auth_jwt() -> str:
    algorithm: str = "RS512"
    headers: dict = {
        "alg": algorithm,
        "typ": "JWT",
        "kid": os.getenv("NOTIFY_API_KID")
    }
    api_key: str = os.getenv("NOTIFY_API_KEY")

    payload: dict = {
        "sub": api_key,
        "iss": api_key,
        "jti": str(uuid.uuid4()),
        "aud": os.getenv("OAUTH2_TOKEN_URL"),
        "exp": int(time.time()) + 300,  # 5mins in the future
    }

    private_key = get_private_key(os.getenv("PRIVATE_KEY_PATH", "private.pem"))

    return generate_jwt(
            algorithm, private_key, headers,
            payload, expiry_minutes=5
        )


def generate_jwt(
    algorithm: str,
    private_key,
    headers: dict,
    payload: dict,
    expiry_minutes: int = None,
) -> str:
    if expiry_minutes:
        expiry_date = (
            datetime.datetime.now(datetime.timezone.utc) +
            datetime.timedelta(minutes=expiry_minutes)
        )
        payload["exp"] = expiry_date

    return jwt.encode(payload, private_key, algorithm, headers)


def get_private_key(private_key_path: str) -> str:
    with open(private_key_path, "r", encoding="utf-8") as f:
        private_key = f.read()
        return private_key
