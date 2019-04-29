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

import logging
import os
import re
import shutil
import time

from distroinfo import exception
from distroinfo import helpers
from distroinfo.helpers import git


log = logging.getLogger("distroinfo")


class GitRepoManager(object):
    repo_desc = u'git'

    def __init__(self,
                 base_path,
                 url,
                 repo_dir_postfix=None,
                 ttl=None):
        self.base_path = os.path.abspath(base_path)
        self.url = url
        self.repo_dir_postfix = repo_dir_postfix
        _, _, self.repo_name = url.rpartition('/')
        self.ttl = ttl
        if not self.repo_name:
            raise exception.RepoError(
                what=u"Failed to parse %s repo URL: %s" % (self.repo_desc,
                                                           self.url))
        self.repo_path = os.path.join(
            self.base_path,
            self.repo_name + self.repo_dir_postfix or '')

    def nuke(self):
        log.warn(u"Removing %s repo: %s" % (self.repo_desc, self.repo_path))
        shutil.rmtree(self.repo_path, ignore_errors=True)

    def clone(self):
        log.info(u"Cloning {desc} repo: {url}\n"
                 u"        {space} into: {path}".format(
                     desc=self.repo_desc,
                     space=len(self.repo_desc) * ' ',
                     url=self.url,
                     path=self.repo_path))
        git('clone', self.url, self.repo_path)

    def get_last_fetch_time(self):
        path = os.path.join(self.repo_path, '.git/FETCH_HEAD')
        if os.path.exists(path):
            return os.path.getmtime(path)
        # FETCH_HEAD isn't available on fresh clone
        path = os.path.join(self.repo_path, '.git')
        if os.path.exists(path):
            return os.path.getmtime(path)
        return None

    def fetch(self, force=False):
        need_fetch = True
        with self.repo_dir():
            delta = 0
            if not force and self.ttl:
                try:
                    # caching enabled, check for last repo fetch
                    t_fetch = self.get_last_fetch_time()
                    delta = int(time.time()) - t_fetch
                    if delta < self.ttl:
                        need_fetch = False
                        log.info(u"Existing %s repo is fresh enough, "
                                 u"it was fetched %d s ago: %s" % (
                                     self.repo_desc, delta, self.repo_path))
                    else:
                        log.info(u"Existing %s repo is too old, "
                                 u"it was fetched %d s ago: %s" % (
                                     self.repo_desc, delta, self.repo_path))
                except Exception as e:
                    raise e
            if need_fetch:
                log.info(u"Fetching %s repo: %s" % (self.repo_desc,
                                                    self.repo_path))
                git('fetch', 'origin')
                git('checkout', '-f', 'master')
                git('reset', '--hard', 'origin/master')

    def repo_dir(self):
        """
        Use

            with self.repo_dir():
                commands

        to temporarily set current directory to repo path"""
        return helpers.cdir(self.repo_path)

    def get_file_path(self, fn):
        return os.path.join(self.repo_path, fn)

    def check_remote(self):
        assert self.url
        with self.repo_dir():
            remotes = git('remote', '-v')
        pattern = r'^origin\s+%s\s+\(fetch\)$' % re.escape(self.url)
        if not re.search(pattern, remotes, re.MULTILINE):
            raise exception.RepoError(what="origin isn't set to expected URL: "
                                           "%s" % self.url)

    def sync(self, force_fetch=False):
        if not self.url:
            if not os.path.isdir(self.repo_path):
                raise exception.NotADirectory(path=self.repo_path)
            return
        if self.base_path and not os.path.isdir(self.base_path):
            log.info(u"Creating base directory: %s" % self.base_path)
            os.makedirs(self.base_path)
        if not os.path.isdir(self.repo_path):
            self.clone()
        else:
            try:
                self.check_remote()
            except exception.RepoError as e:
                log.warn(u"%s repo didn't pass the checks, renewing: %s"
                         % (self.repo_desc, e))
                self.nuke()
                self.clone()
            else:
                self.fetch(force=force_fetch)
