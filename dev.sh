#!/bin/bash

# Install Azure Functions Core Tools before running
# See: https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?pivots=python-mode-decorators&tabs=linux%2Cbash%2Cazure-cli%2Cbrowser#install-the-azure-functions-core-tools
# Add the relevant package repository then run:
# sudo apt-get install azure-functions-core-tools-4

ENV_FILE=".env.local"

source ${ENV_FILE}

echo "Migrating database to latest version..."
ENV_FILE=${ENV_FILE} alembic -c src/notify/alembic.ini upgrade head

echo "Starting the API function app..."
cd src/notify && ENV_FILE="../../${ENV_FILE}" func start --verbose
