import logging
import os
import psycopg2
import time

SCHEMA_FILE_PATH = f"{os.path.dirname(__file__)}/../../../../database/schema.sql"
SCHEMA_INITIALISED_SQL = """
    SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'channel_statuses')
"""


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
    logging.debug(f"Connected to database in {(end - start)}s")

    check_and_initialise_schema(conn)

    return conn


def check_and_initialise_schema(conn: psycopg2.extensions.connection):
    if bool(os.getenv("SCHEMA_INITIALISED")):
        return

    with conn.cursor() as cur:
        cur.execute(SCHEMA_INITIALISED_SQL)
        if not bool(cur.fetchone()[0]):
            logging.info("Initialising schema")
            cur.execute(open(SCHEMA_FILE_PATH, "r").read())

    conn.commit()
    os.environ["SCHEMA_INITIALISED"] = "true"
