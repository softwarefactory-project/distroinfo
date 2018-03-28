import hashlib
import os
import yaml

from distroinfo import exception
from distroinfo import helpers
from distroinfo import repoman


def get_id(s, postfix=False):
    h = hashlib.sha1(s.encode()).hexdigest()[:4]
    if postfix:
        h = '-' + h
    return h


class InfoFetcher(object):
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
    def __init__(self, *args, **kwargs):
        self.cache_ttl = kwargs.pop('cache_ttl', 0)
        self.cache_base_path = kwargs.pop('cache_base_path', None)
        if not self.cache_base_path:
            self.cache_base_path = helpers.get_default_cache_base_path()
        super(CachedInfoFetcher, self).__init__(*args, **kwargs)

    def get_file_content(self, fn):
        raise NotImplementedError()


class LocalInfoFetcher(InfoFetcher):
    def get_file_content(self, fn):
        fn = os.path.join(self.source, fn)
        return open(fn).read()


class RemoteInfoFetcher(CachedInfoFetcher):
    def get_file_content(self, fn):
        # TODO: fetch raw files
        raise NotImplementedError()


class RemoteGitInfoFetcher(CachedInfoFetcher):
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
