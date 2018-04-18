import hashlib
import logging
import os
import requests
import yaml

from distroinfo import exception
from distroinfo import helpers
from distroinfo import repoman


logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("distroinfo")


def get_id(s, postfix=False):
    h = hashlib.sha1(s.encode()).hexdigest()[:4]
    if postfix:
        h = '-' + h
    return h


class InfoFetcher(object):
    """
    Abstract class to derive simple info fetchers from.

    Implement get_file_content() to return info file contents.

    See CachedInfoFetcher if you also need caching.
    """
    def __init__(self, source, allow_import=True):
        self.source = source
        self.allow_import = allow_import
        self.fetching = set()

    def get_file_content(self, fn):
        raise NotImplementedError()

    def get_file_data(self, fn):
        content = self.get_file_content(fn)
        return yaml.load(content)

    def fetch(self, *info_files):
        contents = []
        for ifn in info_files:
            if ifn in self.fetching:
                raise exception.CircularInfoInclude(fn=ifn)
            info = self.get_file_data(ifn)
            contents.append(info)
            # handle includes recursively
            imports = info.get('import', [])
            if self.allow_import and imports:
                self.fetching.add(ifn)
                try:
                    contents += self.fetch(*imports)
                finally:
                    self.fetching.remove(ifn)
        return contents


class CachedInfoFetcher(InfoFetcher):
    """
    Abstract class to derive caching info fetchers from.

    Implement get_file_content() to return info file contents.

    Only cache if self.cache_ttl > 0.
    """
    def __init__(self, *args, **kwargs):
        self.cache_ttl = kwargs.pop('cache_ttl', 0)
        self.cache_base_path = kwargs.pop('cache_base_path', None)
        if not self.cache_base_path:
            self.cache_base_path = helpers.get_default_cache_base_path()
        super(CachedInfoFetcher, self).__init__(*args, **kwargs)

    def get_file_content(self, fn):
        raise NotImplementedError()


class LocalInfoFetcher(InfoFetcher):
    """Fetch info files from local directory (source)"""
    def get_file_content(self, fn):
        fn = os.path.join(self.source, fn)
        return open(fn).read()


class RemoteInfoFetcher(CachedInfoFetcher):
    """
    Fetch remote info files from URL (source)

    Cache info files locally if self.cache_ttl > 0
    """
    def __init__(self, *args, **kwargs):
        super(RemoteInfoFetcher, self).__init__(*args, **kwargs)
        self.cache_path = os.path.join(
            self.cache_base_path, get_id(self.source))

    def fetch_file(self, fn):
        url = u'%s%s' % (self.source, fn)
        log.info(u'Fetching remote file: %s' % url)
        req = requests.get(url)
        if req.ok:
            if self.cache_ttl:
                # cache this file
                helpers.ensure_dir(self.cache_path)
                path = os.path.join(self.cache_path, fn)
                open(path, 'wt').write(req.text)
            return req.text
        else:
            raise exception.RemoteFetchError(
                code=req.status_code, reason=req.reason, url=url)

    def get_file_content(self, fn):
        path = os.path.join(self.cache_path, fn)
        fetch = True
        if self.cache_ttl and os.path.exists(path):
            # look for cache first
            age = helpers.get_file_age(path)
            if age <= self.cache_ttl:
                # use cached version
                fetch = False
                log.info(u'Using %d s old cached version of %s' % (age, fn))
        if fetch:
            text = self.fetch_file(fn)
        else:
            text = open(path, 'rt').read()
        return text


class RemoteGitInfoFetcher(CachedInfoFetcher):
    """
    Fetch info files from a remote git repo (source)

    Use git clone to get the repository.

    Only sync the repo if local copy is older than self.cache_ttl
    """
    def __init__(self, *args, **kwargs):
        super(RemoteGitInfoFetcher, self).__init__(*args, **kwargs)
        self.repo = repoman.GitRepoManager(
            url=self.source,
            ttl=self.cache_ttl,
            base_path=self.cache_base_path,
            repo_dir_postfix=get_id(self.source, postfix=True))
        self.synced = False

    def get_file_content(self, fn):
        if not self.synced:
            self.repo.sync()
            self.synced = True
        path = self.repo.get_file_path(fn)
        return open(path).read()

    @property
    def cache_path(self):
        return self.repo.repo_path
