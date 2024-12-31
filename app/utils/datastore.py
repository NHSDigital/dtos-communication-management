import logging
import os
import psycopg2
import app.utils.schema_initialiser as schema_initialiser
import time
from typing import Tuple


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
    INSERT INTO {status_table} (
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


def create_batch_message_record(batch_message_data: dict) -> Tuple[str, str] | None | bool:
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_BATCH_MESSAGE, batch_message_data)
                return cur.fetchone()

    except psycopg2.Error as e:
        logging.error("Error creating batch message record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def create_status_record(status_data: dict, is_channel_status=False) -> bool | str:
    status_table = "channel_statuses" if is_channel_status else "message_statuses"
    statement = INSERT_STATUS.format(status_table=status_table)
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(statement, status_data)

                return cur.fetchone()[0]

    except psycopg2.Error as e:
        logging.error("Error creating message status record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def connection() -> psycopg2.extensions.connection:
    start = time.time()
    conn = psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        host=os.environ["DATABASE_HOST"],
        password=os.environ["DATABASE_PASSWORD"],
        sslmode=os.getenv("DATABASE_SSLMODE", "require"),
    )
    end = time.time()
    logging.debug(f"Connected to database in {(end - start)}s")

    schema_initialiser.check_and_initialise_schema(conn)

    return conn
