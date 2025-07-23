from app import cache
from app.models import Consumer
from app.utils.database import engine
from sqlalchemy.orm import Session


def fetch(key: str) -> Consumer | None:
    return fetch_all().get(key)


@cache.memoize()
def fetch_all() -> dict[str, Consumer]:
    mapping = {}

    with Session(engine()) as session:
        for c in session.query(Consumer).all():
            mapping[c.key] = c

    return mapping
