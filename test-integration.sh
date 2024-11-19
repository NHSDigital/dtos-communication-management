#!/bin/bash
docker compose --env-file .env.test run --build integration-tests pytest -v /tests/integration
test_exit_code=$?
docker compose --env-file .env.test down db --volumes
exit $test_exit_code

