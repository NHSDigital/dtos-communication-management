import dotenv
import logging
import os
import psycopg2
import time

from azure.identity import DefaultAzureCredential

AZURE_AAD_URL = "https://ossrdbms-aad.database.windows.net"
TOKEN_EXPIRY = 86400

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


def initialise_database():
    schema_file = f"{root_path()}/database/create_database.sql"
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute(open(schema_file, "r").read())

        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        logging.error("Error creating database schema")
        logging.error(f"{type(e).__name__} : {e}")


def connection():
    return psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        host=os.environ["DATABASE_HOST"],
        password=fetch_database_password(),
    )


def fetch_database_password():
    dotenv.load_dotenv()

    if float(os.getenv("DATABASE_PASSWORD_EXPIRES", "0")) > time.time():
        save_credentials(
            DefaultAzureCredential().get_token(AZURE_AAD_URL).token,
            time.time() + TOKEN_EXPIRY,
        )

    return os.getenv("DATABASE_PASSWORD")


def save_credentials(token: str, expires: float):
    os.environ["DATABASE_PASSWORD"] = token
    os.environ["DATABASE_PASSWORD_EXPIRES"] = str(expires)

    with open(f"{root_path()}/.env", "w") as f:
        f.write((
            f"DATABASE_PASSWORD={token}\n" +
            f"DATABASE_PASSWORD_EXPIRES={expires}\n"
        ))


def root_path():
    return os.path.dirname(__file__) + "/../.."
