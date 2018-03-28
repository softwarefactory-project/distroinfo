import contextlib
import os
import subprocess

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
    return os.path.expanduser("~/.distroinfo/cache")


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
    return out
