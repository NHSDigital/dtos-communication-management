import logging
import os
import psycopg2
import time


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

    return conn
