import logging
import os
import psycopg2
import time

BATCH_MESSAGES_EXISTS = """
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'batch_messages')
"""

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

INSERT_MESSAGE_STATUS = """
    INSERT INTO message_statuses (
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

SCHEMA_FILE_PATH = f"{os.path.dirname(__file__)}/database/schema.sql"

def create_batch_message_record(batch_message_data: dict) -> bool | list[str, str]:
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_BATCH_MESSAGE, batch_message_data)
                return cur.fetchone()

        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        logging.error("Error creating batch message record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def create_message_status_record(message_status_data: dict) -> bool | str:
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_MESSAGE_STATUS, message_status_data)

                return cur.fetchone()[0]

        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        logging.error("Error creating message status record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def connection():
    start = time.time()
    conn = psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        host=os.environ["DATABASE_HOST"],
        password=os.environ["DATABASE_PASSWORD"],
        sslmode=os.getenv("DATABASE_SSLMODE", "require"),
    )
    end = time.time()
    logging.info(f"Connected to database in {(end - start)}s")

    check_and_initialise_schema(conn)

    return conn


def check_and_initialise_schema(conn: psycopg2.extensions.connection):
    if bool(os.getenv("SCHEMA_INITIALISED")):
        return

    with conn.cursor() as cur:
        cur.execute(BATCH_MESSAGES_EXISTS)
        if not bool(cur.fetchone()[0]):
            logging.info("Initialising schema")
            cur.execute(open(SCHEMA_FILE_PATH, "r").read())

    conn.commit()
    os.environ["SCHEMA_INITIALISED"] = "true"
