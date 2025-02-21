import logging
import os
import psycopg2
import time
from sqlalchemy import create_engine
from sqlalchemy import URL


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


# TODO: Determine whether to memoize the engine
def engine():
    return create_engine(connection_url())


def connection_url():
    return URL.create(
        "postgresql+psycopg2",
        username=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        host=os.environ["DATABASE_HOST"],
        database=os.environ["DATABASE_NAME"],
        query={"sslmode": os.getenv("DATABASE_SSLMODE", "require")},
    )
