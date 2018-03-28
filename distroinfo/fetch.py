import os
import yaml

import exception


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
                    # TODO: test (recursive) includes
                    self.fetching.remove(ifn)
        return contents


class LocalInfoFetcher(InfoFetcher):
    def get_file_content(self, fn):
        fn = os.path.join(self.source, fn)
        return open(fn).read()


class RemoteRawInfoFetcher(InfoFetcher):
    def get_file_content(self, fn):
        # TODO: fetch raw files
        raise NotImplementedError()


class RemoteGitInfoFetcher(InfoFetcher):
    def get_file_content(self, fn):
        # TODO: fetch from git (port from rdopkg)
        raise NotImplementedError()
