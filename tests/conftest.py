import app.cache as cache
import app.models as models
import app.utils.database as database
import app.services.message_batch_recorder as message_batch_recorder
import dotenv
import flask
import logging
import os
import psycopg2
import pytest
import app.utils.uuid_generator as uuid_generator
from sqlalchemy.orm import Session


if not bool(os.getenv("CI")):
    dotenv.load_dotenv(".env.test")


# Inserts the human readable docstring as the nodeid for the test
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    test_fn = item.obj
    docstring = getattr(test_fn, '__doc__')

    if docstring:
        report.nodeid = docstring

        location = list(report.location)
        location[0] = f"{docstring} {location[0]}"
        report.location = tuple(location)


def pytest_addoption(parser):
    parser.addoption('--truncatedb-scope', action='store', default='function')


def determine_truncatedb_scope(fixture_name, config):
    return config.getoption("--truncatedb-scope", "function")


@pytest.fixture(autouse=True, scope=determine_truncatedb_scope)
def truncatedb():
    if os.getenv("NO_DB") == "true":
        return

    try:
        with database.connection() as conn:
            with conn.cursor() as cur:
                cur.execute((
                    "TRUNCATE TABLE "
                    "consumers, message_batches, messages, "
                    "channel_statuses, message_statuses "
                    "RESTART IDENTITY"
                ))
                cur.connection.commit()
    except psycopg2.OperationalError as e:
        logging.error(f"Error: {e}")


@pytest.fixture
def message_batch_post_body():
    # Generate message reference using the reference_uuid function
    message_ref = uuid_generator.reference_uuid("4010232137.Thursday 03 February 2022.10:00am")

    return {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "routingPlanId": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                "messageBatchReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                "messages": [
                    {
                        "messageReference": message_ref,
                        "recipient": {
                            "nhsNumber": "4010232137",
                            "contactDetails": {
                                "email": "recipient@nhs.net",
                                "sms": "07777777777",
                                "address": {
                                    "lines": [
                                        "NHS England",
                                        "6th Floor",
                                        "7&8 Wellington Place",
                                        "Leeds",
                                        "West Yorkshire"
                                    ],
                                    "postcode": "LS1 4AP"
                                }
                            }
                        },
                        "originator": {
                            "odsCode": "X26"
                        },
                        "personalisation": {}
                    }
                ]
            }
        }
    }


@pytest.fixture
def message_batch_post_response():
    # Generate message reference using the reference_uuid function
    message_ref = uuid_generator.reference_uuid("4010232137.Thursday 03 February 2022.10:00am")

    return {
        "data": {
            "type": "MessageBatch",
            "id": "2ZljUiS8NjJNs95PqiYOO7gAfJb",
            "attributes": {
                "messageBatchReference": "da0b1495-c7cb-468c-9d81-07dee089d728",
                "routingPlan": {
                    "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                    "name": "Plan Abc",
                    "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp",
                    "createdDate": "2023-11-17T14:27:51.413Z"
                },
                "messages": [
                    {
                        "messageReference": message_ref,
                        "id": "2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                    }
                ]
            }
        }
    }


@pytest.fixture
def channel_status_post_body():
    return {
        "data": [
            {
                "type": "ChannelStatus",
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "703b8008-545d-4a04-bb90-1f2946ce1575",
                    "cascadeType": "primary",
                    "cascadeOrder": 1,
                    "channel": "nhsapp",
                    "channelStatus": "delivered",
                    "channelStatusDescription": " ",
                    "supplierStatus": "read",
                    "timestamp": "2023-11-17T14:27:51.413Z",
                    "retryCount": 1
                },
                "links": {
                    "message": "https://api.service.nhs.uk/comms/v1/messages/2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                },
                "meta": {
                    "idempotencyKey": "2515ae6b3a08339fba3534f3b17cd57cd573c57d25b25b9aae08e42dc9f0a445" #gitleaks:allow
                }
            }
        ]
    }


@pytest.fixture
def message_status_post_body():
    # Generate message reference using the reference_uuid function
    message_ref = uuid_generator.reference_uuid("4010232137.Thursday 03 February 2022.10:00am")

    return {
        "data": [
            {
                "type": "MessageStatus",
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": message_ref,
                    "messageStatus": "sending",
                    "messageStatusDescription": " ",
                    "channels": [
                        {
                            "type": "email",
                            "channelStatus": "delivered"
                        }
                    ],
                    "timestamp": "2023-11-17T14:27:51.413Z",
                    "routingPlan": {
                        "id": "b838b13c-f98c-4def-93f0-515d4e4f4ee1",
                        "name": "Plan Abc",
                        "version": "ztoe2qRAM8M8vS0bqajhyEBcvXacrGPp",
                        "createdDate": "2023-11-17T14:27:51.413Z"
                    }
                },
                "links": {
                    "message": "https://api.service.nhs.uk/comms/v1/messages/2WL3qFTEFM0qMY8xjRbt1LIKCzM"
                },
                "meta": {
                    "idempotencyKey": "2515ae6b3a08339fba3534f3b17cd57cd573c57d25b25b9aae08e42dc9f0a445" #gitleaks:allow
                }
            }
        ]
    }

@pytest.fixture
def consumer():
    with Session(database.engine()) as session:
        consumer = session.query(models.Consumer).filter_by(key="some-consumer").one_or_none()
        if not consumer:
            consumer = models.Consumer(key="some-consumer")
            session.add(consumer)
        session.commit()
        yield consumer

@pytest.fixture
def teardown_consumer():
    with Session(database.engine()) as session:
        consumer = session.query(models.Consumer).filter_by(key="some-consumer").one_or_none()
        if consumer:
            session.delete(consumer)
        session.commit()

@pytest.fixture
def message_batch(consumer, message_batch_post_body, message_batch_post_response):
    message_batch_recorder.save_batch(
        message_batch_post_body,
        message_batch_post_response,
        models.MessageBatchStatuses.SENT,
        consumer.id
    )

@pytest.fixture
def app():
    app = flask.Flask(__name__)
    app.testing = True
    cache.init_app(app)
    return app
