import os

ASSETS_PATH = "tests/assets"
INFO_ASSETS_PATH = "%s/info" % ASSETS_PATH


def get_test_info_path(name):
    return os.path.join(INFO_ASSETS_PATH, name)


def assert_dict_contains(tested, expected):
    for key, val in expected.items():
        assert key in tested
        assert tested[key] == val
