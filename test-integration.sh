#!/bin/bash
docker compose --env-file .env.test run --build integration-tests pytest /tests/integration
docker compose --env-file .env.test down db --volumes
