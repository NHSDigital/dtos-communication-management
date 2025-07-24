import hmac
import json
import os
import app.services.consumer_fetcher as consumer_fetcher
import app.validators.schema_validator as schema_validator
import app.utils.hmac_signature as hmac_signature

API_KEY_HEADER_NAME = 'x-api-key'
AUTHORIZATION_HEADER_NAME = 'authorization'
SIGNATURE_HEADER_NAME = 'x-hmac-sha256-signature'
CONSUMER_KEY_NAME = 'x-consumer-key'


def verify_callback_headers(headers: dict) -> tuple[bool, str]:
    lc_headers = header_keys_to_lower(headers)
    if lc_headers.get(API_KEY_HEADER_NAME) is None:
        return False, "Missing API key header"

    if lc_headers.get(API_KEY_HEADER_NAME) != notify_api_key():
        return False, "Invalid API key"

    if lc_headers.get(SIGNATURE_HEADER_NAME) is None:
        return False, "Missing signature header"

    return True, ""


def verify_headers(headers: dict) -> tuple[bool, str]:
    lc_headers = header_keys_to_lower(headers)
    if lc_headers.get(AUTHORIZATION_HEADER_NAME) is None:
        return False, "Missing Authorization header"
    if lc_headers.get(API_KEY_HEADER_NAME) is None:
        return False, "Missing API key header"
    if lc_headers.get(API_KEY_HEADER_NAME) != consumer_api_key():
        return False, "Invalid API key"
    if lc_headers.get(CONSUMER_KEY_NAME) is None:
        return False, "Missing Consumer key header"
    if consumer_fetcher.fetch(lc_headers.get(CONSUMER_KEY_NAME)) is None:
        return False, "Invalid Consumer key"

    return True, ""


def verify_signature(headers: dict, body: dict, signature: str) -> bool:
    lc_headers = header_keys_to_lower(headers)
    body_str = json.dumps(body, sort_keys=True)

    expected_signature = hmac_signature.create_digest(signature, body_str)

    return hmac.compare_digest(
        expected_signature,
        lc_headers[SIGNATURE_HEADER_NAME],
    )


def verify_body(body: dict) -> tuple[bool, str]:
    return schema_validator.validate_with_schema(body)


def signature_secret() -> str:
    return f"{os.getenv('APPLICATION_ID')}.{notify_api_key()}"


def header_keys_to_lower(headers: dict) -> dict:
    return {k.lower(): v for k, v in headers.items()}


def consumer_api_key():
    return os.getenv("CLIENT_API_KEY")


def notify_api_key():
    return os.getenv("NOTIFY_API_KEY")
