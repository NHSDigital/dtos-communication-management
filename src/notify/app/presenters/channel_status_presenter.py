def as_json(channel_status):
    return {
        "created_at": channel_status.created_at,
        "message_id": channel_status.message_id,
        "message_reference": channel_status.message_reference,
        "channel": channel_status.details["data"][0]["attributes"]["channel"],
        "channelStatus": channel_status.details["data"][0]["attributes"]["channelStatus"],
        "supplierStatus": channel_status.details["data"][0]["attributes"]["supplierStatus"],
    }
