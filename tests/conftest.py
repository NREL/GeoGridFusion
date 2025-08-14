import os
import geogridfusion  # replace with actual module name


def pytest_configure():
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("Using CI database config: monkeypatching start()")
        geogridfusion.start = geogridfusion.startup._start_test
