import logging
import os
import re
import shutil
import time

from distroinfo import exception
from distroinfo import helpers
from distroinfo.helpers import git


logging.basicConfig(level=logging.ERROR)
log = logging.getLogger("distroinfo-repo")


class GitRepoManager(object):
    repo_desc = 'git'

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
                what="Failed to parse %s repo URL: %s" % (self.repo_desc,
                                                          self.url))
        self.repo_path = os.path.join(
            self.base_path,
            self.repo_name + self.repo_dir_postfix or '')

    def _nuke(self):
        log.warn("Removing %s repo: %s" % (self.repo_desc, self.repo_path))
        shutil.rmtree(self.repo_path, ignore_errors=True)

    def _clone(self):
        log.info("Cloning {desc} repo: {url}\n"
                 "        {space} into: {path}".format(
                     desc=self.repo_desc,
                     space=len(self.repo_desc) * ' ',
                     url=self.url,
                     path=self.repo_path))
        with helpers.cdir(self.base_path):
            git('clone', self.url, self.repo_path)

    def _fetch(self, force=False):
        need_fetch = True
        with self.repo_dir():
            if not force and self.ttl:
                try:
                    t_fetch = os.path.getmtime('.git/FETCH_HEAD')
                    t_now = int(time.time())
                    delta = t_now - t_fetch
                    if delta < self.ttl:
                        need_fetch = False
                except Exception:
                    pass
            if need_fetch:
                log.info("Fetching %s repo: %s" % (self.repo_desc,
                                                   self.repo_path))
                git('fetch', 'origin')
                git('checkout', '-f', 'master')
                git('reset', '--hard', 'origin/master')

    def repo_dir(self):
        return helpers.cdir(self.repo_path)

    def get_file_path(self, fn):
        return os.path.join(self.repo_path, fn)

    def check_remote(self):
        assert self.url
        with self.repo_dir():
            remotes = git('remote', '-v')
        pattern = '^origin\s+%s\s+\(fetch\)$' % re.escape(self.url)
        if not re.search(pattern, remotes, re.MULTILINE):
            raise exception.RepoError(what="origin isn't set to expected URL: "
                                           "%s" % self.url)

    def sync(self, force_fetch=False):
        if not self.url:
            if not os.path.isdir(self.repo_path):
                raise exception.NotADirectory(path=self.repo_path)
            return
        if self.base_path and not os.path.isdir(self.base_path):
            log.info("Creating base directory: %s" % self.base_path)
            os.makedirs(self.base_path)
        if not os.path.isdir(self.repo_path):
            self._clone()
        else:
            try:
                self.check_remote()
            except exception.RepoError as e:
                log.warn("%s repo didn't pass the checks, renewing: %s"
                         % (self.repo_desc, e))
                self._nuke()
                self._clone()
            else:
                self._fetch(force=force_fetch)
