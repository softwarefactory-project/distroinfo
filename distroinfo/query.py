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

from __future__ import print_function
from functools import partial
import re
import six

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from distroinfo import exception


def get_release(info, release):
    for rls in info['releases']:
        if rls.get('name') == release:
            return rls
    return None


def get_package(info, name):
    for pkg in info['packages']:
        if pkg['name'] == name:
            return pkg
    return None


def find_package(info, package, strict=False):
    # 1. strict package name matching (openstack-nova)
    pkg = get_package(info, package)
    if pkg:
        return pkg
    # 2. strict project/upstream matching (nova, git://../openstack/nova)
    ps = strip_project_url(package)
    for pkg in info['packages']:
        if 'project' in pkg and pkg['project'].lower() == ps:
            return pkg
        if 'upstream' in pkg:
            upstream = pkg['upstream']
            if strip_project_url(upstream) == ps:
                return pkg
    if strict:
        return None
    # 3. best effort
    is_url = re.search(r'\W', ps)
    psl = ps.lower()
    if is_url:
        for pkg in info['packages']:
            if 'project' in pkg and pkg['project'].lower() in psl:
                return pkg
    for pkg in info['packages']:
        if psl in pkg['name'].lower():
            return pkg
    return None


def find_element(info, needle, info_key='osp_releases'):
    '''Find a matching needle in a custom list of dict'''
    if info_key not in info:
        return None

    for elem in info[info_key]:
        finding = __find_element(elem, needle)
        if finding:
            return elem
    return None


def __find_element(data, needle):
    '''Helper for recursions, used by find_element()'''
    for elem in data:
        if isinstance(data, dict):
            elem = data[elem]
        if needle in elem:
            return data
        if isinstance(elem, list) or isinstance(elem, dict):
            res = __find_element(elem, needle)
            return res
    return None


def filter_pkgs(pkgs, rexen):
    filter_wrapper = partial(_match_pkg, rexen)
    return list(filter(filter_wrapper, pkgs))


def _match_pkg(rexen, pkg):
    for attr, rex in rexen.items():
        val = pkg.get(attr)
        if val is None:
            return False
        if isinstance(val, six.string_types):
            if not re.search(rex, val):
                return False
        elif isinstance(val, Iterable):
            # collection matches if any item of collection matches
            found = False
            for e in val:
                if re.search(rex, e):
                    found = True
                    break
            if not found:
                return False
        else:
            raise exception.InvalidPackageFilter(
                why=("Can only filter strings but '%s' is %s"
                     % (attr, type(rex).__name__)))
    return True


def get_distrepos(info, release, dist=None):
    # release is required now, but this function can be extended to
    # return distrepos for multiple releases if needed
    rls = get_release(info, release)
    if not rls:
        why = 'release not defined in rdoinfo: %s' % release
        raise exception.InvalidQuery(why=why)
    found_dist = False
    distrepos = []
    for repo in rls['repos']:
        if dist and repo['name'] != dist:
            continue
        dr = repo.get('distrepos')
        if dr:
            distrepos.append((release, repo['name'], dr))
            if dist:
                found_dist = True
                break
    if dist and not found_dist:
        why = 'dist not defined in rdoinfo: %s/%s' % (release, dist)
        raise exception.InvalidQuery(why=why)
    if not distrepos:
        why = 'No distrepos information in rdoinfo for %s' % release
        raise exception.InvalidQuery(why=why)

    return distrepos


def tags_diff(info1, info2, tagsname='tags'):
    changedpkgs = []
    for pkg2 in info2["packages"]:
        if pkg2 not in info1["packages"]:
            changedpkgs.append(pkg2)
    diff = []
    for pkg2 in changedpkgs:
        foundpkg = False
        for pkg1 in info1["packages"]:
            if pkg1['project'] == pkg2['project']:
                foundpkg = True
                break
        updated_tags = []
        if foundpkg:
            for tag in pkg2.get(tagsname, {}):
                # use address of this function to differentiate
                # between missing tag and tag: None
                tag1 = pkg1.get(tagsname, {}).get(tag, tags_diff)
                if pkg2[tagsname][tag] != tag1:
                    updated_tags.append(tag)
        else:
            if pkg2.get(tagsname):
                updated_tags = list(pkg2.get(tagsname).keys())
        if updated_tags:
            diff.append((pkg2['name'], updated_tags))
    return diff


def attr_diff(info1, info2, attrname):
    """
    Check for differences in a given attribute between two DistroInfo objects.

       :param DistroInfo info1: initial DistroInfo object to compare with
       :param DistroInfo info2: target DistroInfo object to compare
       :param str attrname: attribute to check for changes

    Returns list of tuples, in the format: ('package-name', 'new-attr-value')
    """
    changedpkgs = []
    for pkg2 in info2["packages"]:
        if pkg2 not in info1["packages"]:
            changedpkgs.append(pkg2)
    diff = []
    for pkg2 in changedpkgs:
        foundpkg = False
        for pkg1 in info1["packages"]:
            if pkg1['project'] == pkg2['project']:
                foundpkg = True
                break
        updated_attrs = None
        if foundpkg:
            attr1 = pkg1.get(attrname)
            if pkg2.get(attrname) != attr1:
                updated_attrs = pkg2.get(attrname)
        else:
            if pkg2.get(attrname):
                updated_attrs = pkg2.get(attrname)
        if updated_attrs:
            diff.append((pkg2['name'], updated_attrs))
    return diff


def strip_project_url(url):
    """strip proto:// | openstack/ prefixes and .git | -distgit suffixes"""
    m = re.match(r'(?:[^:]+://)?(.*)', url)
    if m:
        url = m.group(1)
    if url.endswith('.git'):
        url, _, _ = url.rpartition('.')
    if url.endswith('-distgit'):
        url, _, _ = url.rpartition('-')
    if url.startswith('openstack/'):
        # openstack is always special :-p
        _, _, url = url.partition('/')
    return url
