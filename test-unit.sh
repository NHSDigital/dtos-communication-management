#!/bin/bash

pytest -vv tests/unit || {
    echo "Tests failed in tests/unit"
    exit 1
}
