import app.models as models
import app.utils.database as database
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
                    details=request_body,
                    idempotency_key=meta["idempotencyKey"],
                    message_id=attributes["messageId"],
                    message_reference=attributes["messageReference"],
                    status=attributes.get("messageStatus", attributes.get("supplierStatus")),
                ))

            session.commit()

        return True
    except Exception as e:
        logging.error("Error saving statuses: %s", e)
        return False
