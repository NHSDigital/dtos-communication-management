import json
from jsonschema import validate, ValidationError
import os

schema_path = os.path.dirname(os.path.abspath(__file__)) + "/schemas/"
schema = json.load(open(schema_path + "nhs-notify.json"))
schema_path_identifiers = {
    "MessageBatch": "/v1/message-batches",
    "ChannelStatus": "/\u003Cclient-provided-channel-status-URI\u003E",
    "MessageStatus": "/\u003Cclient-provided-message-status-URI\u003E",
}


def validate_with_schema(schema_type: str, data: dict) -> tuple[bool, str]:
    """Validate against the specified schema."""
    try:
        validate(instance=data, schema=schema_for_type(schema_type))
        return True, ""
    except ValidationError as e:
        return False, e.message


def schema_for_type(schema_type: str):
    """Return schema for the specified type."""
    return subschema(schema_path_identifiers[schema_type])


def subschema(identifier: str):
    """Look up subschema for the specified identifier."""
    return schema["paths"][identifier]["post"]["requestBody"]["content"]["application/vnd.api+json"]["schema"]
