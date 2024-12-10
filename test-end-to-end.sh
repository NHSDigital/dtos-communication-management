#!/bin/bash
docker compose --env-file .env.test --profile test-end-to-end run --build --quiet-pull end-to-end-tests pytest --cov=src --cov-append /tests/end_to_end
test_exit_code=$?
docker compose --env-file .env.test --profile test-end-to-end down --volumes --remove-orphans
exit $test_exit_code
