import hashlib
import uuid


def uuid4_str() -> str:
    return str(uuid.uuid4())


def reference_uuid(val) -> str:
    str_val = str(val)
    return str(uuid.UUID(hashlib.md5(str_val.encode()).hexdigest()))
