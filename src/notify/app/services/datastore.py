import app.utils.database as database
import logging
import psycopg2

INSERT_BATCH_MESSAGE = """
    INSERT INTO batch_messages (
        batch_id,
        details,
        message_reference,
        nhs_number,
        recipient_id,
        status
    ) VALUES (
        %(batch_id)s,
        %(details)s,
        %(message_reference)s,
        %(nhs_number)s,
        %(recipient_id)s,
        %(status)s
    ) RETURNING batch_id, message_reference"""

INSERT_STATUS = """
    INSERT INTO {table_name} (
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
    ) RETURNING idempotency_key"""

STATUS_TABLE_NAMES_BY_TYPE = {
    "ChannelStatus": "channel_statuses",
    "MessageStatus": "message_statuses"
}


def create_batch_message_record(batch_message_data: dict) -> bool | list[str, str]:
    try:
        with database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_BATCH_MESSAGE, batch_message_data)
                return cur.fetchone()

    except psycopg2.Error as e:
        logging.error("Error creating batch message record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def create_status_record(status_type: str, status_data: dict) -> bool | str:
    table_name = STATUS_TABLE_NAMES_BY_TYPE[status_type]
    try:
        with database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_STATUS.format(table_name=table_name), status_data)

                return cur.fetchone()[0]

    except psycopg2.Error as e:
        logging.error("Error creating status record")
        logging.error(f"{type(e).__name__} : {e}")
        return False
