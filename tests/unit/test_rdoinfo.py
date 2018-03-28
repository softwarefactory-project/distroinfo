from distroinfo.info import DistroInfo
from distroinfo import query

import test_common as common


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
            'git://git.openstack.org/openstack/nova',
        'patches':
            'http://review.rdoproject.org/r/p/openstack/nova.git',
        'distgit':
            'https://github.com/rdo-packages/nova-distgit.git',
        'master-distgit':
            'https://github.com/rdo-packages/nova-distgit.git',
        'review-origin':
            'ssh://review.rdoproject.org:29418/openstack/nova-distgit.git',
        'review-patches':
            'ssh://review.rdoproject.org:29418/openstack/nova.git',
    }
    common.assert_dict_contains(pkg, expected=nova)
    assert 'tags' in pkg
    assert 'buildsys-tags' in pkg
    assert 'maintainers' in pkg


def assert_rdoinfo_deps(info):
    """
    Make sure data from rdoinfo rdo.yml file is parsed correctly
    by checking python-sphinx dependency packages.

    NOTE: this needs to be kept in sync with rdoinfo
    """
    pkg = query.get_package(info, 'python-sphinx')
    assert pkg
    nova = {
        'name': 'python-sphinx',
        'project': 'python-sphinx',
        'conf': 'rdo-dependency',
        'upstream': 'https://github.com/sphinx-doc/sphinx',
        'patches': None,
        'distgit': 'https://github.com/rdo-common/python-sphinx.git',
    }
    common.assert_dict_contains(pkg, expected=nova)
    assert 'tags' in pkg
    assert 'dependency' in pkg['tags']
    assert 'buildsys-tags' in pkg
    assert 'maintainers' in pkg


def test_rdo_base():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    assert_rdoinfo_base(info)


def test_rdo_full():
    di = DistroInfo('rdo-full.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    assert_rdoinfo_base(info)
    assert_rdoinfo_deps(info)


def test_rdo_merge():
    di = DistroInfo(['rdo.yml', 'deps.yml'],
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    assert_rdoinfo_base(info)
    assert_rdoinfo_deps(info)
