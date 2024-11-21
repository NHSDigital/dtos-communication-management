#!/bin/bash
docker compose --env-file .env.test --profile test-integration run --build integration-tests pytest -v /tests/integration
test_exit_code=$?
docker compose --env-file .env.test --profile test-integration down db --volumes
exit $test_exit_code
