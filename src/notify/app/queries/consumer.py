from functools import cache
from sqlalchemy.orm import Session
from app.models import Consumer
from app.utils.database import engine


def fetch_from_cache(key: str) -> Consumer | None:
    return indexed_by_key().get(key)


def indexed_by_key() -> dict[str, Consumer]:
    index = {}

    for c in fetch_all_cached():
        index[c.key] = c

    return index


@cache
def fetch_all_cached() -> list[Consumer]:
    return fetch_all()


def fetch_all() -> list[Consumer]:
    with Session(engine()) as session:
        consumers = session.query(Consumer).all()

    return consumers
