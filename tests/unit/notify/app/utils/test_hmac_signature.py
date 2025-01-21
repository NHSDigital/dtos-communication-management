import app.utils.hmac_signature as hmac_signature
import hmac
import hashlib


def test_valid_hmac_signature():
    """Test a valid HMAC signature matches."""
    secret = 'secret'
    message = 'message'

    expected_signature = hmac.new(
        bytes(secret, 'ASCII'),
        msg=bytes(message, 'ASCII'),
        digestmod=hashlib.sha256
    ).hexdigest()

    actual_signature = hmac_signature.create_digest(secret, message)

    assert hmac.compare_digest(expected_signature, actual_signature)


def test_unmatched_message_in_hmac_signature():
    """Test that a different message creates a different signature."""
    secret = 'secret'
    message = 'message'

    expected_signature = hmac.new(
        bytes(secret, 'ASCII'),
        msg=bytes("nope", 'ASCII'),
        digestmod=hashlib.sha256
    ).hexdigest()

    actual_signature = hmac_signature.create_digest(secret, message)

    assert not hmac.compare_digest(expected_signature, actual_signature)

def test_unmatched_secret_in_hmac_signature():
    """Test that a different secret creates a different signature"""
    secret = 'secret'
    message = 'message'

    expected_signature = hmac.new(
        bytes("nope", 'ASCII'),
        msg=bytes(message, 'ASCII'),
        digestmod=hashlib.sha256
    ).hexdigest()

    actual_signature = hmac_signature.create_digest(secret, message)

    assert not hmac.compare_digest(expected_signature, actual_signature)
