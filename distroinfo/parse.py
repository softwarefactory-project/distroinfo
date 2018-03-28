import collections
import copy
import six

from distroinfo import exception


def parse_info(raw_info, apply_tag=None):
    """
    Parse raw rdoinfo metadata inplace.

    :param apply_tag: tag to apply
    :returns: dictionary containing all packages in rdoinfo
    """
    parse_releases(raw_info)
    parse_packages(raw_info, apply_tag=apply_tag)
    return raw_info


def parse_release_repo(repo, default_branch=None):
    if 'name' not in repo:
        raise exception.MissingRequiredItem(item='repo.name')
    if 'branch' not in repo:
        if default_branch:
            repo['branch'] = default_branch
        else:
            raise exception.MissingRequiredItem(item='repo.branch')
    return repo


def parse_releases(info):
    try:
        releases = info['releases']
    except KeyError:
        raise exception.MissingRequiredSection(section='releases')
    if not isinstance(releases, collections.Iterable):
        raise exception.InvalidInfoFormat(
            msg="'releases' section must be a list")
    for rls in releases:
        try:
            rls_name = rls['name']
        except KeyError:
            raise exception.MissingRequiredItem(item='release.name')
        try:
            repos = rls['repos']
        except KeyError:
            raise exception.MissingRequiredItem(item='release.builds')
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
        raise exception.MissingRequiredItem(item='package.name')
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


def check_for_duplicates(pkg, pkgs):
    for oldpkg in pkgs:
        if pkg['name'] == oldpkg['name']:
            return True
    return False


def parse_packages(info, apply_tag=None):
    try:
        pkgs = info['packages']
    except KeyError:
        raise exception.MissingRequiredSection(section='packages')
    if not isinstance(pkgs, collections.Iterable):
        raise exception.InvalidInfoFormat(
            msg="'packages' section must be a list")

    parsed_pkgs = []
    for pkg in pkgs:
        parsed_pkg = parse_package(pkg, info, apply_tag=apply_tag)
        if check_for_duplicates(parsed_pkg, parsed_pkgs):
            raise exception.DuplicatedProject(prj=parsed_pkg['name'])
        else:
            parsed_pkgs.append(parsed_pkg)

    info['packages'] = parsed_pkgs


def _merge(a, b):
    # recursively merge arbitrary data structures
    if isinstance(a, dict) and isinstance(b, dict):
        m = dict(a)
        m.update({k: _merge(a.get(k, None), b[k]) for k in b})
        return m

    if isinstance(a, list) and isinstance(b, list):
        return a + b

    if b is None:
        return a
    return b


def merge_infos(*infos):
    if not infos:
        return infos
    info = infos[0]
    for info2 in infos[1:]:
        info = _merge(info, info2)
    return info
