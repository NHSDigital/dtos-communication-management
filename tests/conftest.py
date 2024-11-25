import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    test_fn = item.obj
    docstring = getattr(test_fn, '__doc__')

    if docstring:
        report.nodeid = docstring

        location = list(report.location)
        location[0] = docstring
        report.location = tuple(location)
