import io
import os
import logging

from distroinfo import query


ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
INFO_ASSETS_PATH = os.path.join(ASSETS_PATH, 'info')


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


def assert_rdoinfo_base(info):
    """
    Make sure data from rdoinfo rdo.yml file is parsed correctly
    by checking the flagship nova package.

    NOTE: this needs to be kept in sync with rdoinfo
    """
    pkg = query.get_package(info, 'openstack-nova')
    assert pkg
    nova = {
        'name': 'openstack-nova',
        'project': 'nova',
        'conf': 'rpmfactory-core',
        'upstream':
            'https://opendev.org/openstack/nova',
        'patches':
            'http://review.rdoproject.org/r/openstack/nova.git',
        'distgit':
            'https://github.com/rdo-packages/nova-distgit.git',
        'master-distgit':
            'https://github.com/rdo-packages/nova-distgit.git',
        'review-origin':
            'ssh://review.rdoproject.org:29418/openstack/nova-distgit.git',
        'review-patches':
            'ssh://review.rdoproject.org:29418/openstack/nova.git',
    }
    assert_dict_contains(pkg, expected=nova)
    assert 'tags' in pkg
    assert 'component' in pkg
    assert 'maintainers' in pkg


def assert_rdoinfo_deps(info):
    """
    Make sure data from rdoinfo rdo.yml file is parsed correctly
    by checking python-sphinx dependency packages.

    NOTE: this needs to be kept in sync with rdoinfo
    """
    pkg = query.get_package(info, 'python-sphinx')
    assert pkg
    sphinx = {
        'name': 'python-sphinx',
        'project': 'python-sphinx',
        'conf': 'rdo-dependency',
        'upstream': 'https://github.com/sphinx-doc/sphinx',
        'patches': None,
        'distgit': 'https://github.com/rdo-common/python-sphinx',
    }
    assert_dict_contains(pkg, expected=sphinx)
    assert 'tags' in pkg
    assert 'dependency' in pkg['tags']
    assert 'buildsys-tags' in pkg
    assert 'maintainers' in pkg


def assert_rdoinfo_full(info):
    assert_rdoinfo_base(info)
    assert_rdoinfo_deps(info)
