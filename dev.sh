#!/bin/bash

docker compose --env-file .env.local --profile test build
docker compose --env-file .env.local --profile test up
