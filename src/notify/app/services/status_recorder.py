import app.models as models
import app.utils.database as database
import json
import logging
from sqlalchemy.orm import Session


def save_statuses(request_body: dict) -> bool:
    try:
        with Session(database.engine()) as session:
            for status_data in request_body["data"]:
                status_model = models.ChannelStatus if status_data["type"] == "ChannelStatus" else models.MessageStatus
                meta = status_data["meta"]
                attributes = status_data["attributes"]

                session.add(status_model(
                    details=json.dumps(request_body, sort_keys=True),
                    idempotency_key=meta["idempotencyKey"],
                    message_id=attributes["messageId"],
                    message_reference=attributes["messageReference"],
                    status=attributes.get("messageStatus", attributes.get("channelStatus")),
                ))

            session.commit()

        return True
    except Exception as e:
        logging.error(f"Error saving statuses: {e}")
        return False
