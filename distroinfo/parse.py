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

import collections
import copy
import six

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from distroinfo import exception


def parse_info(raw_info, apply_tag=None):
    """
    Parse raw rdoinfo metadata inplace.

    :param raw_info: raw info to parse
    :param apply_tag: tag to apply
    :returns: dictionary containing all packages in rdoinfo
    """
    parse_releases(raw_info)
    parse_packages(raw_info, apply_tag=apply_tag)
    return raw_info


def parse_release_repo(repo, default_branch=None):
    if 'name' not in repo:
        raise exception.MissingRequiredItem(item='repo.name in %s' % repo)
    if 'branch' not in repo:
        if default_branch:
            repo['branch'] = default_branch
        else:
            raise exception.MissingRequiredItem(
                item='repo.branch for repo %s' % repo['name'])
    return repo


def parse_releases(info):
    try:
        releases = info['releases']
    except KeyError:
        raise exception.MissingRequiredSection(section='releases')
    if not isinstance(releases, Iterable):
        raise exception.InvalidInfoFormat(
            msg="'releases' section must be iterable")
    if isinstance(releases, dict):
        releases = releases.values()
    for rls in releases:
        try:
            rls_name = rls['name']
        except KeyError:
            raise exception.MissingRequiredItem(
                item='release.name in %s' % rls)
        try:
            repos = rls['repos']
        except KeyError:
            raise exception.MissingRequiredItem(
                item='release.repos for release %s' % rls_name)
        default_branch = rls.get('branch')
        for repo in repos:
            parse_release_repo(repo, default_branch)
    return releases


def parse_package_configs(info):
    if 'package-default' not in info:
        info['package-default'] = {}
    if 'package-configs' not in info:
        info['package-configs'] = {}
    return info['package-default'], info['package-configs']


def substitute_package(pkg):
    # substitution is very simple, no recursion
    # feel free to extend this as long as you provide proper tests
    new_pkg = copy.copy(pkg)
    for key, val in pkg.items():
        if isinstance(val, six.string_types):
            try:
                new_pkg[key] = val % pkg
            except KeyError:
                raise exception.SubstitutionFailed(txt=val)
    return new_pkg


def parse_package(pkg, info, apply_tag=None):
    pkddefault, pkgconfs = parse_package_configs(info)
    # start with default package config
    parsed_pkg = copy.deepcopy(pkddefault)
    if 'conf' in pkg:
        # apply package configuration template
        conf_id = pkg['conf']
        try:
            conf = pkgconfs[conf_id]
        except KeyError:
            raise exception.UndefinedPackageConfig(conf=conf_id)
        parsed_pkg.update(conf)
    parsed_pkg.update(pkg)
    if apply_tag:
        tags = parsed_pkg.get('tags', {})
        tagdict = tags.get(apply_tag)
        if tagdict:
            parsed_pkg.update(tagdict)
    pkg = substitute_package(parsed_pkg)

    try:
        name = pkg['name']
    except KeyError:
        raise exception.MissingRequiredItem(item='package.name in %s' % pkg)
    if 'project' not in pkg:
        raise exception.MissingRequiredItem(
            item="project for '%s' package" % name)
    try:
        maints = pkg['maintainers']
    except KeyError:
        raise exception.MissingRequiredItem(
            item="maintainers for '%s' package" % name)
    if not maints:
        raise exception.MissingRequiredItem(
            item="at least one maintainer for '%s' package" % name)
    try:
        for maint in maints:
            if '@' not in maint:
                raise exception.InvalidInfoFormat(
                    msg="'%s' doesn't look like maintainer's email." % maint)
    except TypeError:
        raise exception.InvalidInfoFormat(
            msg='package.maintainers must be a list of email addresses')

    return pkg


def _check_for_duplicates(pkg, pkgs):
    for oldpkg in pkgs:
        if pkg['name'] == oldpkg['name']:
            return True
    return False


def parse_packages(info, apply_tag=None):
    try:
        pkgs = info['packages']
    except KeyError:
        raise exception.MissingRequiredSection(section='packages')
    if not isinstance(pkgs, Iterable):
        raise exception.InvalidInfoFormat(
            msg="'packages' section must be iterable")
    if isinstance(pkgs, dict):
        # 'packages' is a dictionary
        info_dicts = True
        parsed_pkgs = collections.OrderedDict()
        pkgs = pkgs.values()
    else:
        # 'packages' is a list
        info_dicts = False
        parsed_pkgs = []
        seen_projects = []
    for pkg in pkgs:
        parsed_pkg = parse_package(pkg, info, apply_tag=apply_tag)
        project = parsed_pkg['project']
        if info_dicts:
            parsed_pkgs[project] = parsed_pkg
        else:
            if project in seen_projects:
                raise exception.DuplicatedProject(prj=parsed_pkg['project'])
            seen_projects.append(project)
            parsed_pkgs.append(parsed_pkg)
    info['packages'] = parsed_pkgs


def _merge(a, b):
    # recursively merge arbitrary data structures
    if isinstance(a, dict) and isinstance(b, dict):
        m = a.copy()
        m.update({k: _merge(a.get(k, None), b[k]) for k in b})
        return m

    if isinstance(a, list) and isinstance(b, list):
        return a + b

    if b is None:
        return a
    return b


def list2dict(_list, key):
    d = collections.OrderedDict()
    for i in _list:
        kv = i.get(key)
        if kv in d:
            d[kv] = _merge(d[kv], i)
        else:
            d[kv] = i
    return d


def info2dicts(info, in_place=False):
    """
    Return info with:

    1) `packages` list replaced by a 'packages' dict indexed by 'project'
    2) `releases` list replaced by a 'releases' dict indexed by 'name'
    """
    if 'packages' not in info and 'releases' not in info:
        return info
    if in_place:
        info_dicts = info
    else:
        info_dicts = info.copy()
    packages = info.get('packages')
    if packages:
        info_dicts['packages'] = list2dict(packages, 'project')
    releases = info.get('releases')
    if releases:
        info_dicts['releases'] = list2dict(releases, 'name')
    return info_dicts


def info2lists(info, in_place=False):

    """
    Return info with:

    1) `packages` dict replaced by a 'packages' list with indexes removed
    2) `releases` dict replaced by a 'releases' list with indexes removed

    info2list(info2dicts(info)) == info
    """
    if 'packages' not in info and 'releases' not in info:
        return info
    if in_place:
        info_lists = info
    else:
        info_lists = info.copy()
    packages = info.get('packages')
    if packages:
        info_lists['packages'] = list(packages.values())
    releases = info.get('releases')
    if releases:
        info_lists['releases'] = list(releases.values())
    return info_lists


def merge_infos(*infos, **kwargs):
    if not infos:
        return {}
    info_dicts = kwargs.get('info_dicts', False)
    in_place = kwargs.get('in_place', True)
    if len(infos) == 1:
        if info_dicts:
            return info2dicts(infos[0], in_place=in_place)
        return infos[0]
    info_dict = info2dicts(infos[0], in_place=in_place)
    for info_next in infos[1:]:
        info_next_dict = info2dicts(info_next, in_place=in_place)
        info_dict = _merge(info_dict, info_next_dict)
    if info_dicts:
        # return info with dicts
        return info_dict
    # convert info back to lists format
    return info2lists(info_dict, in_place=in_place)
