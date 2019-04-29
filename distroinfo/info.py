# Copyright (c) 2019 Red Hat
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import six

from distroinfo import exception
from distroinfo import fetch
from distroinfo import parse


class DistroInfo(object):
    def __init__(self,
                 info_files,
                 fetcher=None,
                 local_info=None,
                 remote_info=None,
                 remote_git_info=None,
                 cache_ttl=3600,
                 cache_base_path=None):
        """
        Specify distroinfo instance to query.

        :param info_files: info file name or a list of file names
        :param fetcher: custom info fetcher,
                        implementation of distroinfo.fetch.InfoFetcher,
                        you can use *_info params instead for builtins
        :param local_info: a shortcut to use LocalInfoFetcher
        :param remote_info: a shortcut to use RemoteRawInfoFetcher
        :param remote_git_info: a shortcut use RemoteGitInfoFetcher
        """
        if fetcher:
            self.fetcher = fetcher
        else:
            # convenience shortcuts to builtin info fetchers
            if local_info:
                self.fetcher = fetch.LocalInfoFetcher(local_info)
            elif remote_info:
                self.fetcher = fetch.RemoteInfoFetcher(
                    remote_info,
                    cache_ttl=cache_ttl,
                    cache_base_path=cache_base_path)
            elif remote_git_info:
                self.fetcher = fetch.RemoteGitInfoFetcher(
                    remote_git_info,
                    cache_ttl=cache_ttl,
                    cache_base_path=cache_base_path)
            else:
                raise exception.InfoFetcherRequired()
        self.fetcher.di_class = DistroInfo
        self.info_files = info_files

        if isinstance(self.info_files, six.string_types):
            # support both a single file and a list
            self.info_files = [self.info_files]

    def get_info(self, apply_tag=None, info_dicts=False):
        """
        Get data from distroinfo instance.

        :param apply_tag: apply supplied tag to info
        :param info_dicts: return packages and releases as dicts
        :return: parsed info metadata
        """
        raw_infos = self.fetcher.fetch(*self.info_files)
        raw_info = parse.merge_infos(*raw_infos, info_dicts=info_dicts)
        info = parse.parse_info(raw_info, apply_tag=apply_tag)
        return info
