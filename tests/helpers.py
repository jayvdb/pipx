import sys


def assert_not_in_virtualenv():
    assert not hasattr(sys, "real_prefix"), "Tests cannot run under virtualenv"
    assert getattr(sys, "base_prefix", sys.prefix) != sys.prefix, "Tests require venv"
