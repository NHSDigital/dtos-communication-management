#!/bin/bash
docker compose --env-file .env.test --profile test run --build --quiet-pull end-to-end-tests pytest /tests/end_to_end
test_exit_code=$?
docker compose --env-file .env.test --profile test down --volumes --remove-orphans
exit $test_exit_code
