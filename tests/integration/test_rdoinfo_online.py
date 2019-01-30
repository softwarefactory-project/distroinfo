from distroinfo.info import DistroInfo
from distroinfo import query
import re

import tests.test_common as common


RDOINFO_GIT_URL = 'https://github.com/redhat-openstack/rdoinfo'
RDOINFO_RAW_URL = ('https://raw.githubusercontent.com/'
                   'redhat-openstack/rdoinfo/master/')


def test_rdoinfo_remote_fetch(tmpdir):
    log_stream = common.capture_distroinfo_logger()
    remote_di = DistroInfo('rdo-full.yml',
                           remote_info=RDOINFO_RAW_URL,
                           cache_base_path=str(tmpdir))
    # first fetch
    remote_info = remote_di.get_info()
    out = log_stream.getvalue()
    assert 'Fetching remote file:' in out
    # NOTE(jpena): with the current rdoinfo structure, we import tags.yml
    # twice, so it would fail the assertion
    # assert 'cached' not in out
    common.assert_rdoinfo_full(remote_info)
    # second fetch should be cached
    remote_info = remote_di.get_info()
    out = log_stream.getvalue()
    assert re.search(r'Using \d+ s old cached version of [^\n]+$', out)
    common.assert_rdoinfo_full(remote_info)
    # also load and parse the local repo copy (cache) using local fetcher
    cached_di = DistroInfo('rdo-full.yml',
                           local_info=remote_di.fetcher.cache_path)
    cached_info = cached_di.get_info()
    common.assert_rdoinfo_full(cached_info)
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
    common.assert_rdoinfo_full(git_info)
    # second fetch with the same instance uses the already synced repo
    # without additional checks
    log_stream = common.capture_distroinfo_logger()
    git_info = git_di.get_info()
    assert log_stream.getvalue() == ''
    common.assert_rdoinfo_full(git_info)
    # a followup fetch with a new instance should reuse previously synced repo
    # after ttl checks
    git_di = DistroInfo('rdo-full.yml',
                        remote_git_info=RDOINFO_GIT_URL,
                        cache_base_path=str(tmpdir))
    git_info = git_di.get_info()
    out = log_stream.getvalue()
    assert u"git repo is fresh" in out
    assert u"Cloning git repo" not in out
    assert u"Fetching git repo" not in out
    assert u"git resp is too old" not in out

    common.assert_rdoinfo_full(git_info)
    # also load and parse the local repo copy (cache) using local fetcher
    cached_di = DistroInfo('rdo-full.yml',
                           local_info=git_di.fetcher.cache_path)
    cached_info = cached_di.get_info()
    common.assert_rdoinfo_full(cached_info)
    # make sure results from both fetchers are identical
    assert git_info == cached_info
