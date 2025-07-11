import app.models as models
import app.utils.database as database
import app.utils.uuid_generator as uuid_generator
from collections import defaultdict
from itertools import chain
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


def save_batch(body, response, status, consumer_id) -> tuple[bool, str]:
    try:
        with Session(database.engine(), expire_on_commit=False) as session:
            message_batch = models.MessageBatch(
                batch_id=response["data"]["id"],
                batch_reference=response["data"]["attributes"]["messageBatchReference"],
                consumer_id = consumer_id,
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
    except IntegrityError as e:
        logging.error("Failed to save batch: %s", e.__cause__)
        return False, str(e.__cause__)
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
