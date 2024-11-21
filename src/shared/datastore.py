import logging
import os
import psycopg2


def create_batch_message_record(batch_message_data: dict) -> bool | list[str, str]:
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
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
                    ) RETURNING batch_id, message_reference""", batch_message_data)

                return cur.fetchone()
    except psycopg2.Error as e:
        logging.error("Error creating batch message record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def create_message_status_record(message_status_data: dict) -> bool | str:
    try:
        with connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
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
                    ) RETURNING idempotency_key""", message_status_data)

                return cur.fetchone()[0]

        conn.close()
    except psycopg2.Error as e:
        logging.error("Error creating message status record")
        logging.error(f"{type(e).__name__} : {e}")
        return False


def connection():
    return psycopg2.connect(
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USER"],
        host=os.environ["DATABASE_HOST"],
        password=os.environ["DATABASE_PASSWORD"]
    )
