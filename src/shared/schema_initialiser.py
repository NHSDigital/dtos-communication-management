import os
import psycopg2
import logging


SCHEMA_FILE_PATH = f"{os.path.dirname(__file__)}/database/schema.sql"

# FIXME: This could be replaced with a version number query from a migrations table.
SCHEMA_CHECK = """
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'channel_statuses')
"""


def check_and_initialise_schema(conn: psycopg2.extensions.connection):
    if bool(os.getenv("SCHEMA_INITIALISED")):
        return

    with conn.cursor() as cur:
        cur.execute(SCHEMA_CHECK)
        if not bool(cur.fetchone()[0]):
            logging.debug("Initialising schema")
            cur.execute(open(SCHEMA_FILE_PATH, "r").read())

    conn.commit()
    os.environ["SCHEMA_INITIALISED"] = "true"
