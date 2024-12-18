#!/bin/bash

pytest -W ignore::PendingDeprecationWarning -vv --cov=src --cov-append tests/pacts || {
    echo "Tests failed in tests/pacts"
    exit 1
}
