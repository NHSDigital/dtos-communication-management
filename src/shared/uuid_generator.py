import hashlib
import time
import uuid


def recipient_id(message_data: dict) -> str:
    str_val: str = ",".join([
        message_data["appointment_date"],
        message_data["appointment_time"],
        message_data["date_of_birth"],
        message_data["nhs_number"],
    ])
    return reference_uuid(str_val)


def reference_uuid(val) -> str:
    str_val = str(val)
    return str(uuid.UUID(hashlib.md5(str_val.encode()).hexdigest()))
