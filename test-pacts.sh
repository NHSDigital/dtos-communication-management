#!/bin/bash

pytest -W ignore::PendingDeprecationWarning -vv tests/pacts || {
    echo "Tests failed in tests/pacts"
    exit 1
}
