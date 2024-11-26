import hashlib
import uuid


def recipient_id(message_data: dict) -> str:
    str_val: str = ",".join([
        message_data["nhs_number"],
        message_data["date_of_birth"],
    ])
    return reference_uuid(str_val)


def message_reference(message_data: dict) -> str:
    str_val: str = ",".join([
        message_data["nhs_number"],
        message_data["date_of_birth"],
        message_data["appointment_date"],
        message_data["appointment_time"],
    ])
    return reference_uuid(str_val)


def reference_uuid(val) -> str:
    str_val = str(val)
    return str(uuid.UUID(hashlib.md5(str_val.encode()).hexdigest()))
