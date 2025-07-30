from app.models import Consumer
from app.queries.consumer import fetch_all_cached
import app.utils.database as database
from flask.cli import with_appcontext
import click
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def _create_consumer(key) -> tuple[Consumer, None] | tuple[None, str]:
    try:
        with Session(database.engine(), expire_on_commit=False) as session:
            consumer = Consumer(key=key)
            session.add(consumer)
            session.commit()
            fetch_all_cached.cache_clear()
            print(f"Consumer with key '{consumer.key}' created")
            return (consumer, None)
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            print(f"Consumer with key '{key}' already exists")
        else:
            print(e.orig)
        return (None, str(e.orig))
    except Exception as e:
        print(e)
        return (None, str(e))


@click.command(name="create-consumer")
@click.argument("key")
@with_appcontext
def create_consumer(key):
    """A method to create a new Consumer which takes its key as an argument"""
    _create_consumer(key)
