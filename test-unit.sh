#!/bin/bash

pytest -v --cov=src --cov-append tests/unit || {
    echo "Tests failed in tests/unit"
    exit 1
}
