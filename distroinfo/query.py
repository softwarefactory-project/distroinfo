from __future__ import print_function
import collections
import re

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


def filter_pkgs(pkgs, rexen):
    def _filter(pkg):
        for attr, rex in rexen.items():
            val = pkg.get(attr)
            if val is None:
                return False
            if isinstance(val, basestring):
                if not re.search(rex, val):
                    return False
            elif isinstance(val, collections.Iterable):
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

    return filter(_filter, pkgs)


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
                updated_tags = pkg2.get(tagsname).keys()
        if updated_tags:
            diff.append((pkg2['name'], updated_tags))
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
