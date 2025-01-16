import pytest
import dotenv

dotenv.load_dotenv(".env.test")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    test_fn = item.obj
    docstring = getattr(test_fn, '__doc__')

    if docstring:
        report.nodeid = docstring

        location = list(report.location)
        location[0] = docstring
        report.location = tuple(location)


@pytest.fixture
def channel_status_post_body():
    return {
        "data": [
            {
                "type": "ChannelStatus",
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
                    "cascadeType": "primary",
                    "cascadeOrder": 1,
                    "channel": "nhsapp",
                    "channelStatus": "delivered",
                    "channelStatusDescription": " ",
                    "supplierStatus": "delivered",
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
    return {
        "data": [
            {
                "type": "MessageStatus",
                "attributes": {
                    "messageId": "2WL3qFTEFM0qMY8xjRbt1LIKCzM",
                    "messageReference": "1642109b-69eb-447f-8f97-ab70a74f5db4",
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
