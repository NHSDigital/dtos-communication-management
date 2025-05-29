import app.utils.database as database
import dotenv
import logging
import os
import psycopg2
import pytest
import app.utils.uuid_generator as uuid_generator

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
                cur.execute("TRUNCATE TABLE message_batches, messages, channel_statuses, message_statuses RESTART IDENTITY")
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
def csv_data():
    return [
        'UNUSED_STAGE_COLUMN,4010232137,987654,"BLAKE, KYLIE, MRS",03M02M2001,EP700,03M02M2022,10:00:00,"The Royal Shrewsbury Hospital, Breast Screening Office, Shrewsbury, SY3 8XQ"',
        'UNUSED_STAGE_COLUMN,9876543210,987654,"BLAKE, KAREN, MRS",04M04M2002,EP700,04M04M2024,11:00:00,"The Epping Breast Screening Unit, St Margaret\'s Hospital, The Plain, Epping, Essex, CM16 6TN"',
    ]


# The message_batch_body function should return the following dictionary for the above CSV data:
@pytest.fixture
def expected_message_batch_body():
    # Generate message references using the reference_uuid function
    message_ref_1 = uuid_generator.reference_uuid("4010232137.Thursday 03 February 2022.10:00am")
    message_ref_2 = uuid_generator.reference_uuid("9876543210.Thursday 04 April 2024.11:00am")

    # Generate message batch reference using the reference_uuid function
    routing_plan_id = "f134ef50-3d4d-4fc5-8fab-19087a84349f"
    filename = "HWA NHS App Pilot 002 SPRPT"
    message_batch_ref = uuid_generator.reference_uuid(f"{routing_plan_id}.{filename}")

    return {
        "data": {
            "type": "MessageBatch",
            "attributes": {
                "messageBatchReference": message_batch_ref,
                "routingPlanId": routing_plan_id,
                "messages": [
                    {
                        "messageReference": message_ref_1,
                        "recipient": {
                            "nhsNumber": "4010232137",
                        },
                        "personalisation": {
                            "appointment_date": "Thursday 03 February 2022",
                            "appointment_location": "The Royal Shrewsbury Hospital, Breast Screening Office, Shrewsbury, SY3 8XQ",
                            "appointment_time": "10:00am",
                            "contact_telephone_number": "020 3758 2024",
                            "tracking_id": "4010232137",
                        }
                    },
                    {
                        "messageReference": message_ref_2,
                        "recipient": {
                            "nhsNumber": "9876543210",
                        },
                        "personalisation": {
                            "appointment_date": "Thursday 04 April 2024",
                            "appointment_location": "The Epping Breast Screening Unit, St Margaret's Hospital, The Plain, Epping, Essex, CM16 6TN",
                            "appointment_time": "11:00am",
                            "contact_telephone_number": "020 3758 2024",
                            "tracking_id": "9876543210",
                        }
                    }
                ]
            }
        }
    }
