from distroinfo.info import DistroInfo
from distroinfo import query
import re

import test_common as common


RDOINFO_GIT_URL = 'https://github.com/redhat-openstack/rdoinfo'
RDOINFO_RAW_URL = ('https://raw.githubusercontent.com/'
                   'redhat-openstack/rdoinfo/master/')


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


def assert_rdoinfo_full(info):
    assert_rdoinfo_base(info)
    assert_rdoinfo_deps(info)


def test_rdoinfo_base():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    assert_rdoinfo_base(info)


def test_rdoinfo_full():
    di = DistroInfo('rdo-full.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    assert_rdoinfo_full(info)


def test_rdoinfo_merge():
    di = DistroInfo(['rdo.yml', 'deps.yml'],
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    assert_rdoinfo_full(info)


def test_rdoinfo_remote_fetch(tmpdir):
    log_stream = common.capture_distroinfo_logger()
    remote_di = DistroInfo('rdo-full.yml',
                           remote_info=RDOINFO_RAW_URL,
                           cache_base_path=str(tmpdir))
    # first fetch
    remote_info = remote_di.get_info()
    out = log_stream.getvalue()
    assert 'Fetching remote file:' in out
    assert 'cached' not in out
    assert_rdoinfo_full(remote_info)
    # second fetch should be cached
    remote_info = remote_di.get_info()
    out = log_stream.getvalue()
    assert re.search(r'Using \d+ s old cached version of [^\n]+$', out)
    assert_rdoinfo_full(remote_info)
    # also load and parse the local repo copy (cache) using local fetcher
    cached_di = DistroInfo('rdo-full.yml',
                           local_info=remote_di.fetcher.cache_path)
    cached_info = cached_di.get_info()
    assert_rdoinfo_full(cached_info)
    # make sure results from both fetchers are identical
    assert remote_info == cached_info


def test_rdoinfo_git_fetch(tmpdir):
    log_stream = common.capture_distroinfo_logger()
    git_di = DistroInfo('rdo-full.yml',
                        remote_git_info=RDOINFO_GIT_URL,
                        cache_base_path=str(tmpdir))
    # first fetch should clone the git repo
    git_info = git_di.get_info()
    out = log_stream.getvalue()
    assert u"Cloning git repo" in out
    assert_rdoinfo_full(git_info)
    # second fetch with the same instance uses the already synced repo without additional checks
    log_stream = common.capture_distroinfo_logger()
    git_info = git_di.get_info()
    assert log_stream.getvalue() == ''
    assert_rdoinfo_full(git_info)
    # a followup fetch with a new instance should reuse previously synced repo after ttl checks
    git_di = DistroInfo('rdo-full.yml',
                        remote_git_info=RDOINFO_GIT_URL,
                        cache_base_path=str(tmpdir))
    git_info = git_di.get_info()
    out = log_stream.getvalue()
    assert u"git repo is fresh" in out
    assert u"Cloning git repo" not in out
    assert u"Fetching git repo" not in out
    assert u"git resp is too old" not in out

    assert_rdoinfo_full(git_info)
    # also load and parse the local repo copy (cache) using local fetcher
    cached_di = DistroInfo('rdo-full.yml',
                           local_info=git_di.fetcher.cache_path)
    cached_info = cached_di.get_info()
    assert_rdoinfo_full(cached_info)
    # make sure results from both fetchers are identical
    assert git_info == cached_info
