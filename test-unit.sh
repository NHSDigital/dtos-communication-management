#!/bin/bash

pytest -v tests/unit || {
    echo "Tests failed in tests/unit"
    exit 1
}
