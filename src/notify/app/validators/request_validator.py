import hmac
import json
import os
import app.validators.schema_validator as schema_validator
import app.utils.hmac_signature as hmac_signature

API_KEY_HEADER_NAME = 'x-api-key'
SIGNATURE_HEADER_NAME = 'x-hmac-sha256-signature'


def verify_headers(headers: dict, api_key: str) -> tuple[bool, str]:
    lc_headers = header_keys_to_lower(headers)
    if lc_headers.get(API_KEY_HEADER_NAME) is None:
        return False, "Missing API key header"

    if lc_headers.get(API_KEY_HEADER_NAME) != api_key:
        return False, "Invalid API key"

    if lc_headers.get(SIGNATURE_HEADER_NAME) is None:
        return False, "Missing signature header"

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
    try:
        body_data = body["data"]

        if isinstance(body_data, list):
            if not body_data:
                return False, "Empty data list"

            # Get first item's type
            schema_type = body_data[0]["type"]

            # Verify all items have same type
            if not all(item.get("type") == schema_type for item in body_data):
                return False, "All items must have the same type"
        else:
            schema_type = body_data["type"]

        return schema_validator.validate_with_schema(schema_type, body)
    except KeyError as e:
        return False, f"Invalid body: {e}"
    except IndexError:
        return False, "Invalid body: empty data list"


def signature_secret() -> str:
    return f"{os.getenv('APPLICATION_ID')}.{os.getenv('NOTIFY_API_KEY')}"


def header_keys_to_lower(headers: dict) -> dict:
    return {k.lower(): v for k, v in headers.items()}
