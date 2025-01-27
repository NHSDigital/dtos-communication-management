#!/bin/bash

ENV_FILE=".env.test"

source ${ENV_FILE}

ENV_FILE=${ENV_FILE} alembic upgrade head

./test-setup.sh
./test-unit.sh
./test-integration.sh
