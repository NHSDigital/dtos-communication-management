import app.cache as cache
import app.services.consumer_fetcher as fetcher
from app.utils.database import engine
from app.models import Consumer
from sqlalchemy import select
from sqlalchemy.orm import Session


def test_fetch(app):
    with app.test_request_context():
        consumer = Consumer(key="abc123")

        with Session(engine()) as session:
            session.add(consumer)
            session.commit()

            fetched_consumer = fetcher.fetch("abc123")

            assert fetched_consumer.id == consumer.id
            assert fetched_consumer.key == consumer.key
            assert fetched_consumer.created_at == consumer.created_at


def test_fetch_with_unmatched_key(app):
    assert fetcher.fetch("nope") is None


def test_fetch_all(app):
    consumer = Consumer(key="aaa123")
    another_consumer = Consumer(key="bbb456")

    with Session(engine()) as session:
        session.add(consumer)
        session.add(another_consumer)
        session.commit()

        consumers = session.scalars(select(Consumer)).all()

    consumers_mapping = fetcher.fetch_all()

    for c in consumers:
        mapped_consumer = consumers_mapping[c.key]
        assert mapped_consumer.id == c.id
        assert mapped_consumer.key == c.key
        assert mapped_consumer.created_at == c.created_at


def test_fetch_all_is_memoized(app):
    consumer = Consumer(key="abc123")

    with Session(engine()) as session:
        session.add(consumer)
        session.commit()

        fetched = fetcher.fetch_all()

        assert fetched.get("abc123").id == consumer.id

        another_consumer = Consumer(key="xyz999")

        session.add(another_consumer)
        session.commit()

        refetched = fetcher.fetch_all()

        assert refetched.get("abc123").id == consumer.id
        assert refetched.get("xyz999") is None

        cache.delete_memoized(fetcher.fetch_all)

        fetched_again = fetcher.fetch_all()

        assert fetched_again.get("abc123").id == consumer.id
        assert fetched_again.get("xyz999").id == another_consumer.id
