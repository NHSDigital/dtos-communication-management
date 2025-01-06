
pytest -vv tests/integration || {
    echo "Tests failed in tests/integration"
    exit 1
}
