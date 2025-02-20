#!/bin/sh

ENV_FILE="${ENV_FILE:-.env.test}" alembic upgrade head

pytest --log-cli-level=INFO -vv tests/end_to_end/
