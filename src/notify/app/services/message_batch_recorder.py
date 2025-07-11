import app.models as models
import app.utils.database as database
import app.utils.uuid_generator as uuid_generator
from collections import defaultdict
from itertools import chain
import logging
from sqlalchemy.orm import Session


def save_batch(body, response, status) -> tuple[bool, str]:
    try:
        with Session(database.engine(), expire_on_commit=False) as session:
            message_origin, _ = find_or_create_message_origin(session, response.get("data").get("messageOriginKey"))
            message_batch = models.MessageBatch(
                batch_id=response["data"]["id"],
                batch_reference=response["data"]["attributes"]["messageBatchReference"],
                message_origin_id = message_origin.id if message_origin else None,
                details=body,
                response=response,
                status=status,
            )
            session.add(message_batch)
            session.flush()

            if status == models.MessageBatchStatuses.SENT:
                for message in merged_messages(body, response):
                    message = models.Message(
                        batch_id=message_batch.id,
                        details=message,
                        message_id=message["id"],
                        message_reference=message["messageReference"],
                        nhs_number=message["recipient"]["nhsNumber"],
                        recipient_id=uuid_generator.reference_uuid(message["recipient"]["nhsNumber"]),
                    )
                    session.add(message)

            session.commit()

        return True, f"Batch id: {message_batch.id} saved successfully"
    except Exception as e:
        logging.error("Failed to save batch: %s", e)
        return False, str(e)


def merged_messages(data: dict, response: dict) -> list[dict]:
    message_chain = chain(
        data["data"]["attributes"]["messages"],
        response["data"]["attributes"]["messages"]
    )
    collector = defaultdict(dict)
    for collectible in message_chain:
        collector[collectible["messageReference"]].update(collectible.items())

    return list(collector.values())

def find_or_create_message_origin(session, key) -> tuple[models.MessageOrigin, bool] | tuple[None, None]:
    if key:
        return get_or_create(session, key=key)
    return (None, None)

#  having to do this because Flask doesn't have Django method built in - we might want to make this more generic?
def get_or_create(session, key) -> tuple[models.MessageOrigin, bool]:
    instance = session.query(models.MessageOrigin).filter_by(key=key).one_or_none()
    if instance:
        return instance, False
    else:
        instance = models.MessageOrigin(key=key)
        try:
            session.add(instance)
            session.commit()
        except Exception:
            session.rollback()
            instance = session.query(models.MessageOrigin).filter_by(key=key).one()
            return instance, False
        else:
            return instance, True
