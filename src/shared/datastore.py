import logging
import os
import psycopg2


def create_message_status_record(message_status_data: dict) -> bool:
    data = message_status_data.copy()

    with connection() as conn:
        with conn.cursor() as cur:
            # Check for duplicate idempotency key
            cur.execute("""
                SELECT idempotency_key
                FROM message_statuses
                WHERE idempotency_key = %s
                LIMIT 1
            """, (data["idempotency_key"],))

            if cur.fetchone():
                logging.info(f"Duplicate idempotency key: {data['idempotency_key']}")
                return False

            # If batch_id is not present in the message_status_data, fetch it from the message_statuses table
            # as it should be present from a previous request
            if "batch_id" not in data:
                cur.execute("""
                    SELECT batch_id, nhs_number, recipient_id
                    FROM message_statuses
                    WHERE message_reference = %s
                    LIMIT 1
                """, (data["message_reference"],))

                values = cur.fetchone()
                if not values:
                    logging.info(f"Message reference not found: {data['message_reference']}")
                    return False

                data["batch_id"] = values[0]
                data["nhs_number"] = values[1]
                data["recipient_id"] = values[2]
            else:
                data["message_id"] = None

            cur.execute("""
                INSERT INTO message_statuses (
                    batch_id,
                    idempotency_key,
                    message_id,
                    message_reference,
                    nhs_number,
                    payload,
                    recipient_id,
                    state
                ) VALUES (
                    %(batch_id)s,
                    %(idempotency_key)s,
                    %(message_id)s,
                    %(message_reference)s,
                    %(nhs_number)s,
                    %(payload)s,
                    %(recipient_id)s,
                    %(state)s
                ) RETURNING idempotency_key""", data)

            return cur.fetchone()[0]

    conn.close()


def connection():
    return psycopg2.connect(
        dbname=os.getenv("DATABASE_NAME", "communication_management"),
        user=os.getenv("DATABASE_USER", "postgres"),
        host=os.getenv("DATABASE_HOST", "localhost"),
        password=os.environ["DATABASE_PASSWORD"]
    )
