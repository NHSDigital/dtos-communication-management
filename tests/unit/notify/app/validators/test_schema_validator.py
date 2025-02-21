from app.validators.schema_validator import validate_with_schema


def test_valid_channel_status(channel_status_post_body):
    """Test that the channel status is validated"""

    assert validate_with_schema(channel_status_post_body) == (True, "")


def test_invalid_channel_status(channel_status_post_body):
    """Test that invalid channel status is not validated"""

    channel_status_post_body["data"][0]["attributes"]["channelStatus"] = "invalid"
    error_message = "'invalid' is not one of ['created', 'sending', 'delivered', 'failed', 'skipped']"

    assert validate_with_schema(channel_status_post_body) == (False, error_message)


def test_valid_message_status(message_status_post_body):
    """Test that the message status is validated"""

    assert validate_with_schema(message_status_post_body) == (True, "")


def test_invalid_message_status(message_status_post_body):
    """Test that invalid message status is not validated"""

    message_status_post_body["data"][0]["attributes"]["messageStatus"] = "invalid"
    error_message = "'invalid' is not one of ['created', 'pending_enrichment', 'enriched', 'sending', 'delivered', 'failed']"

    assert validate_with_schema(message_status_post_body) == (False, error_message)


def test_valid_message_batch(message_batch_post_body):
    """Test that the message batch is validated"""

    assert validate_with_schema(message_batch_post_body) == (True, "")


def test_invalid_message_batch(message_batch_post_body):
    """Test that invalid message batch is not validated"""

    message_batch_post_body["data"]["attributes"]["routingPlanId"] = 1234
    error_message = "1234 is not of type 'string'"

    assert validate_with_schema(message_batch_post_body) == (False, error_message)
