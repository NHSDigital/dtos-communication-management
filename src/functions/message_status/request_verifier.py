import hashlib
import hmac
import os

API_KEY_HEADER_NAME = 'x-api-key'
SIGNATURE_HEADER_NAME = 'x-hmac-sha256-signature'


def verify_headers(headers: dict) -> bool:
    if (headers.get(API_KEY_HEADER_NAME) is None or
            headers.get(API_KEY_HEADER_NAME) != os.getenv('OAUTH2_API_KEY')):
        return False

    if headers.get(SIGNATURE_HEADER_NAME) is None:
        return False

    return True


def verify_signature(headers: dict, body: str) -> bool:
    expected_signature = hmac.new(
        bytes(signature_secret(), 'utf-8'),
        msg=bytes(body, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    return expected_signature == headers[SIGNATURE_HEADER_NAME]


def signature_secret() -> str:
    return f"{os.getenv('APPLICATION_ID')}.{os.getenv('OAUTH2_API_KEY')}"
