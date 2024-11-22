#!/bin/bash

docker compose --env-file .env.local --profile dev up --build
