#!/bin/bash

# Run the tests and generate XML
pytest --cov=src -vv \
    --junitxml=unit-test-results.xml \
    --html=unit-test-results.html \
    tests/unit || {
    echo "Tests failed in tests/unit"
    exit 1
}

# Pretty print the XML
python3 tests/scripts/pretty_print_xml.py unit-test-results.xml
