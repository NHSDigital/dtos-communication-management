#!/bin/bash

pytest -W ignore::PendingDeprecationWarning -cov=src -vv tests/pacts || {
    echo "Tests failed in tests/pacts"
    exit 1
}
