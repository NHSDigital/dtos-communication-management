from azure.identity import DefaultAzureCredential
import logging
import os
import psycopg2
import time


AZURE_AAD_URL = "https://ossrdbms-aad.database.windows.net/.default"

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
        password=fetch_database_password(),
    )
    end = time.time()
    logging.info(f"Connected to database in {(end - start)}s")
    return conn


def fetch_database_password():
    logging.info("Fetching database password from environment variable")
    if bool(os.getenv("DATABASE_PASSWORD")):
        logging.info("Fetched database password from environment variable")
        return os.environ["DATABASE_PASSWORD"]

    start = time.time()
    credential = DefaultAzureCredential()
    token = credential.get_token(AZURE_AAD_URL).token
    end = time.time()
    logging.info(f"Fetched database password in {(end - start)}s")

    return token
