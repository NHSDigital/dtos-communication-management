#!/bin/bash

pytest --cov=src -vv tests/unit || {
    echo "Tests failed in tests/unit"
    exit 1
}
