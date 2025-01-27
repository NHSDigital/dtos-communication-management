import app.utils.database as database
from collections import defaultdict
import database.models as models
from itertools import chain
from sqlalchemy.orm import Session
import uuid


def save_batch(data, response, status) -> tuple[bool, str]:
    try:
        with Session(database.engine(), expire_on_commit=False) as session:
            message_batch = models.MessageBatch(
                batch_id=response["data"]["id"],
                batch_reference=response["data"]["attributes"]["messageBatchReference"],
                details=data,
                response=response,
                status=status,
            )
            session.add(message_batch)
            session.flush()

            for message in merged_messages(data, response):
                message = models.Message(
                    batch_id=message_batch.id,
                    details=message,
                    message_id=message["id"],
                    message_reference=message["messageReference"],
                    nhs_number=message["recipient"]["nhsNumber"],
                    recipient_id=str(uuid.uuid4()),
                )
                session.add(message)

            session.commit()

        return True, f"Batch id: {message_batch.id} saved successfully"
    except Exception as e:
        return False, str(e)


def merged_messages(data: dict, response: dict) -> list[dict]:
    message_chain = chain(
        data["attributes"]["messages"],
        response["data"]["attributes"]["messages"]
    )
    collector = defaultdict(dict)
    for collectible in message_chain:
        collector[collectible["messageReference"]].update(collectible.items())

    return list(collector.values())
