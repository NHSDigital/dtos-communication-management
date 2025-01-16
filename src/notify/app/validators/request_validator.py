import hashlib
import hmac
import json
import logging
import os
import app.validators.schema_validator as schema_validator
import app.utils.hmac_signature as hmac_signature

API_KEY_HEADER_NAME = 'x-api-key'
SIGNATURE_HEADER_NAME = 'x-hmac-sha256-signature'


def verify_headers(headers: dict) -> bool:
    lc_headers = header_keys_to_lower(headers)
    if (lc_headers.get(API_KEY_HEADER_NAME) is None or
            lc_headers.get(API_KEY_HEADER_NAME) != os.getenv('NOTIFY_API_KEY')):
        return False

    if lc_headers.get(SIGNATURE_HEADER_NAME) is None:
        return False

    return True


def verify_signature(headers: dict, body: dict) -> bool:
    lc_headers = header_keys_to_lower(headers)
    body_str = json.dumps(body, sort_keys=True)

    expected_signature = hmac_signature.create_digest(signature_secret(), body_str)

    return hmac.compare_digest(
        expected_signature,
        lc_headers[SIGNATURE_HEADER_NAME],
    )


def verify_body(body: dict) -> tuple[bool, str]:
    try:
        schema_type = body["data"][0]["type"]
        return schema_validator.validate_with_schema(schema_type, body)
    except KeyError:
        return False, "Invalid body"


def signature_secret() -> str:
    return f"{os.getenv('APPLICATION_ID')}.{os.getenv('NOTIFY_API_KEY')}"


def header_keys_to_lower(headers: dict) -> dict:
    return {k.lower(): v for k, v in headers.items()}
