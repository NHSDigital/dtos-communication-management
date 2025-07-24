import app.queries.consumer as query
from app.utils.database import engine
from app.models import Consumer
from sqlalchemy.orm import Session


def test_fetch_from_cache():
    consumer = Consumer(key="abc123")

    with Session(engine()) as session:
        session.add(consumer)
        session.commit()

        fetched_consumer = query.fetch_from_cache("abc123")

        assert fetched_consumer.id == consumer.id
        assert fetched_consumer.key == consumer.key
        assert fetched_consumer.created_at == consumer.created_at


def test_fetch_from_cache_with_unmatched_key():
    assert query.fetch_from_cache("nope") is None


def test_indexed_by_key():
    query.fetch_all_cached.cache_clear()

    consumer = Consumer(key="aaa123")
    another_consumer = Consumer(key="bbb456")

    with Session(engine()) as session:
        session.add(consumer)
        session.add(another_consumer)
        session.commit()

        consumers = session.query(Consumer).all()

    indexed_consumers = query.indexed_by_key()

    for c in consumers:
        indexed_consumer = indexed_consumers.get(c.key)
        assert indexed_consumer.id == c.id
        assert indexed_consumer.key == c.key
        assert indexed_consumer.created_at == c.created_at


def test_fetch_all_is_memoized():
    query.fetch_all_cached.cache_clear()

    with Session(engine()) as session:
        session.add(Consumer(key="abc123"))
        session.commit()

        assert len(query.fetch_all_cached()) == 1

        session.add(Consumer(key="def456"))
        session.commit()

        assert len(query.fetch_all_cached()) == 1

        query.fetch_all_cached.cache_clear()

        assert len(query.fetch_all_cached()) == 2
