import datetime
import jwt
import logging
import os
import requests
import time
import uuid

EXPIRES_IN_MINUTES = 5


def get_token() -> str:
    if not os.getenv("OAUTH2_API_KEY"):
        return "awaiting-token"

    auth_jwt: str = generate_auth_jwt()
    headers: dict = {"Content-Type": "application/x-www-form-urlencoded"}

    body = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": auth_jwt,
    }

    response = requests.post(
        str(os.getenv("OAUTH2_TOKEN_URL")),
        data=body,
        headers=headers,
        timeout=10,
    )
    logging.info("Response from OAuth2 token provider: %s", response.status_code)
    response_json = response.json()

    if response.status_code == 200:
        access_token = response_json["access_token"]
    else:
        access_token = ""
        logging.error("Failed to get access token")
        logging.error(response_json)

    return access_token


def generate_auth_jwt() -> str:
    algorithm: str = "RS512"
    headers: dict = {
        "alg": algorithm,
        "typ": "JWT",
        "kid": os.getenv("OAUTH2_API_KID")
    }
    api_key: str | None = os.getenv("OAUTH2_API_KEY")

    payload: dict = {
        "sub": api_key,
        "iss": api_key,
        "jti": str(uuid.uuid4()),
        "aud": os.getenv("OAUTH2_TOKEN_URL"),
        "exp": int(time.time()) + (EXPIRES_IN_MINUTES * 60),
    }

    private_key = os.getenv("PRIVATE_KEY")

    return generate_jwt(
            algorithm, private_key, headers,
            payload, expiry_minutes=EXPIRES_IN_MINUTES
        )


def generate_jwt(
    algorithm: str,
    private_key,
    headers: dict,
    payload: dict,
    expiry_minutes: int | None = None,
) -> str:
    if expiry_minutes:
        expiry_date = (
            datetime.datetime.now(datetime.timezone.utc) +
            datetime.timedelta(minutes=expiry_minutes)
        )
        payload["exp"] = expiry_date

    return jwt.encode(payload, private_key, algorithm, headers)
