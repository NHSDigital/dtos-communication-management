import datastore
import pytest


@pytest.fixture(autouse=True, scope="function")
def truncate_table():
    with datastore.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE batch_messages")
            cur.execute("TRUNCATE TABLE message_statuses")
            cur.connection.commit()
