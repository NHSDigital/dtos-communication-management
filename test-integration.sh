#!/bin/bash
docker compose --env-file .env.test run --build integration-tests pytest -vv --log-cli-level=INFO /tests/integration
docker compose --env-file .env.test down db --volumes

