#!/bin/sh

ENV_FILE="${ENV_FILE:-.env}" alembic upgrade head

pytest --log-cli-level=INFO --truncatedb-scope=module -vv tests/end_to_end/
