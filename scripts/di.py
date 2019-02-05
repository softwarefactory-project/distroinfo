#!/usr/bin/python
"""
Usage: di.py fetch [-C <cache-dir>] [-f remote|git|local] <info-url> <info-file>...
       di.py dump [-y <out.yaml>] [-j <out.json>] [-C <cache-dir>] [-f remote|git|local] <info-url> <info-file>...
       di.py --help | --version

Fetch, parse and dump remote distroinfo metadata.

Commands:
  fetch        fetch specified info into <cache-dir>
  dump         dump parsed info as YAML and/or JSON

Arguments:
  <info-url>   distroinfo repo URL
  <info-file>  info file(s) to parse

Options:
  -f, --fetcher remote|git|local
                             choose a distroinfo fetcher to use
  -y, --yaml-out <out.yaml>  dump parsed info into specified YAML file
  -j, --json-out <out.json>  dump parsed info into specified YAML file
  -C, --cache-dir <dir>      directory to store cached distroinfo metadata
  --version                  show distroinfo version
  -h, --help                 show usage help
"""  # noqa
# NOTE: docopt module is required to run this
# -*- encoding: utf-8 -*-
from __future__ import print_function
from docopt import docopt
import json
from timeit import default_timer as timer
import sys
import yaml

from distroinfo import __version__
from distroinfo import exception
from distroinfo.info import DistroInfo


def get_distroinfo(info_url, info_files, fetcher=None, cache_dir=None):
    kwargs = {}
    # use desired distroinfo fetcher
    if fetcher == 'local':
        kwargs['local_info'] = info_url
    elif fetcher == 'git':
        kwargs['remote_git_info'] = info_url
    else:
        kwargs['remote_info'] = info_url

    if cache_dir:
        kwargs['cache_base_path'] = cache_dir

    return DistroInfo(info_files, **kwargs)


def fetch(info_url, info_files, fetcher=None, cache_dir=None):
    if fetcher:
        fetch_str = ' %s' % fetcher
    else:
        fetch_str = ''
    print("Starting%s info fetch: %s" % (fetch_str, info_url))
    di = get_distroinfo(info_url, info_files,
                        fetcher=fetcher, cache_dir=cache_dir)
    cache_path = getattr(di.fetcher, 'cache_path', None)
    if cache_path:
        print("Cache: %s" % cache_path)
    t_start = timer()
    info = di.get_info()
    t_end = timer()
    t = t_end - t_start
    print("Fetched and parsed info with %d packages in %.2f s."
          % (len(info['packages']), t))
    return 0


def dump(info_url, info_files, fetcher=None, cache_dir=None,
         yaml_out=None, json_out=None):
    di = get_distroinfo(info_url, info_files,
                        fetcher=fetcher, cache_dir=cache_dir)
    info = di.get_info()
    if yaml_out or json_out:
        if yaml_out:
            print("Dumping YAML to: %s" % yaml_out)
            f = open(yaml_out, 'w')
            yaml.dump(info, f)
        if json_out:
            print("Dumping JSON to: %s" % json_out)
            f = open(json_out, 'w')
            json.dump(info, f)
    else:
        print(yaml.dump(info))
    return 0


def distroinfo(cargs, version=__version__):
    """
    distroinfo Command-Line Interface

    """
    code = 1
    args = docopt(__doc__, argv=cargs)
    try:
        if args['--version']:
            if not version:
                version = 'N/A'
            print(version)
            code = 0
        elif args['fetch']:
            code = fetch(
                info_url=args['<info-url>'],
                info_files=args['<info-file>'],
                cache_dir=args['--cache-dir'],
                fetcher=args['--fetcher'],
            )
        elif args['dump']:
            code = dump(
                info_url=args['<info-url>'],
                info_files=args['<info-file>'],
                yaml_out=args['--yaml-out'],
                json_out=args['--json-out'],
                cache_dir=args['--cache-dir'],
                fetcher=args['--fetcher'],
            )
    except (
            exception.InvalidInfoFormat,
            KeyboardInterrupt,
    ) as ex:
        code = getattr(ex, 'exit_code', code)
        print("")
        print(str(ex) or type(ex).__name__)

    return code


def main():
    """
    distroinfo CLI entry point
    """
    sys.exit(distroinfo(sys.argv[1:]))


if __name__ == '__main__':
    main()
