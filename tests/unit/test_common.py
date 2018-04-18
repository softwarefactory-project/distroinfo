import io
import os
import logging

ASSETS_PATH = "tests/assets"
INFO_ASSETS_PATH = "%s/info" % ASSETS_PATH


def get_test_info_path(name):
    return os.path.join(INFO_ASSETS_PATH, name)


def capture_distroinfo_logger():
    log = logging.getLogger('distroinfo')
    log.setLevel(logging.DEBUG)
    log_stream = io.StringIO()
    h = logging.StreamHandler(log_stream)
    log.addHandler(h)
    return log_stream


def assert_dict_contains(tested, expected):
    for key, val in expected.items():
        assert key in tested
        assert tested[key] == val
