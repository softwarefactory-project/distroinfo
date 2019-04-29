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

import contextlib
import os
import subprocess
import time

from distroinfo import exception


@contextlib.contextmanager
def cdir(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def ensure_dir(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise exception.NotADirectory(path=path)
    else:
        os.makedirs(path)


def get_default_cache_base_path():
    return os.path.expanduser(u"~/.distroinfo/cache")


def get_file_age(path):
    t_mod = os.path.getctime(path)
    t_now = time.time()
    return t_now - t_mod


def git(*cmd):
    cmd = ['git'] + list(cmd)
    try:
        prc = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    except OSError:
        raise exception.CommandNotFound(cmd=cmd[0])
    out, err = prc.communicate()
    if prc.returncode != 0:
        raise exception.CommandFailed(cmd=" ".join(cmd),
                                      code=prc.returncode)
    return out.decode('utf-8')
