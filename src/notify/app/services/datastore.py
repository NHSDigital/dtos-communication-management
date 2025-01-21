import app.utils.database as database
import logging
import psycopg2
from psycopg2 import sql

INSERT_MESSAGE_BATCH = """
    INSERT INTO message_batches (
        batch_id,
        batch_reference,
        details,
        response,
        status
    ) VALUES (
        %(batch_id)s,
        %(batch_reference)s,
        %(details)s,
        %(response)s,
        %(status)s
    ) RETURNING batch_id"""

INSERT_STATUS = sql.SQL("""
    INSERT INTO {table} (
        idempotency_key,
        message_id,
        message_reference,
        details,
        status
    ) VALUES (
        %(idempotency_key)s,
        %(message_id)s,
        %(message_reference)s,
        %(details)s,
        %(status)s
    ) RETURNING idempotency_key""")

STATUS_TABLE_NAMES_BY_TYPE = {
    "ChannelStatus": "channel_statuses",
    "MessageStatus": "message_statuses"
}


def create_message_batch_record(message_batch_data: dict) -> bool | list[str, str]:
    try:
        with database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_MESSAGE_BATCH, message_batch_data)
                return cur.fetchone()

    except psycopg2.Error as e:
        logging.error("Error creating message batch record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def create_status_record(status_type: str, status_data: dict) -> bool | str:
    table_name = STATUS_TABLE_NAMES_BY_TYPE[status_type]
    try:
        with database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_STATUS.format(table=sql.Identifier(table_name)), status_data)

                return cur.fetchone()[0]

    except psycopg2.Error as e:
        logging.error("Error creating status record")
        logging.error(f"{type(e).__name__} : {e}")
        return False
