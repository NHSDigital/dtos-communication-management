#!/bin/bash

# Install Azure Functions Core Tools before running
# See: https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?pivots=python-mode-decorators&tabs=linux%2Cbash%2Cazure-cli%2Cbrowser#install-the-azure-functions-core-tools
# Add the relevant package repository then run:
# sudo apt-get install azure-functions-core-tools-4

cd src/notify && func start --verbose
