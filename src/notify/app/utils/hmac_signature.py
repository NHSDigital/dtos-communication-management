import hmac
import hashlib


def create_digest(secret: str, message: str) -> str:
    return hmac.new(
        bytes(secret, 'ASCII'),
        msg=bytes(message, 'ASCII'),
        digestmod=hashlib.sha256
    ).hexdigest()
