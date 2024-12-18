import copy
import six
import unittest
from distroinfo.info import DistroInfo
from distroinfo import query

import tests.test_common as common


def test_attr_diff_base():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    info2 = copy.deepcopy(info)
    # Update distgit for nova
    for pkg in info2['packages']:
        if pkg['project'] == 'nova':
            pkg['upstream'] = 'https://opendev.org/openstack/foo'

    diff = query.attr_diff(info, info2, 'upstream')
    assert (len(diff) == 1)
    assert (diff[0][0] == 'openstack-nova')
    assert (diff[0][1] == 'https://opendev.org/openstack/foo')


def test_attr_diff_nochanges():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    info2 = copy.deepcopy(info)
    diff = query.attr_diff(info, info2, 'upstream')
    assert (len(diff) == 0)


def test_attr_diff_nosuchattr():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    info2 = copy.deepcopy(info)
    # Update distgit for nova
    for pkg in info2['packages']:
        if pkg['project'] == 'nova':
            pkg['upstream'] = 'https://opendev.org/openstack/foo'

    diff = query.attr_diff(info, info2, 'fooattr')
    assert (len(diff) == 0)


def test_attr_diff_newpkg():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    info2 = copy.deepcopy(info)
    # Add package
    newpkg = {'project': 'newproject',
              'name': 'openstack-newproject',
              'master-distgit': 'https://github.com/rdo-packages/new-distgit',
              'upstream': 'https://opendev.org/openstack/newproject'}
    info2['packages'].append(newpkg)

    diff = query.attr_diff(info, info2, 'master-distgit')
    assert (len(diff) == 1)
    assert (diff[0][0] == 'openstack-newproject')
    assert (diff[0][1] == 'https://github.com/rdo-packages/new-distgit')


def test_attr_diff_2_diffs():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    info2 = copy.deepcopy(info)
    # Update distgit for nova
    for pkg in info2['packages']:
        if pkg['project'] == 'nova':
            pkg['upstream'] = 'https://opendev.org/openstack/foo'
        if pkg['project'] == 'cinder':
            pkg['upstream'] = 'https://opendev.org/openstack/foo-cinder'

    diff = query.attr_diff(info, info2, 'upstream')
    assert (len(diff) == 2)


def test_find_element_ok():
    di = DistroInfo('minimal.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    finding = query.find_element(info, 'queens',
                                 info_key='releases')

    assert (finding)
    assert (finding == info['releases'][1])


def test_find_element_not_found():
    di = DistroInfo('minimal.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    finding = query.find_element(info, 'aabb',
                                 info_key='releases')
    assert (not finding)


@unittest.skipIf(six.PY2, "Test fails randomly in python2")
def test_find_element_in_sub_dict_list():
    di = DistroInfo('minimal.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    finding = query.find_element(info, 'cloud7-openstack-rocky-testing',
                                 info_key='releases')

    assert (finding)
    assert (finding == info['releases'][0])


def test_single_filter_pkgs_found():
    di = DistroInfo('minimal.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    pkgs = info['packages']

    rexen = {"project": "keystonemiddleware"}
    finding = query.filter_pkgs(pkgs, rexen)

    assert (isinstance(finding, list))
    assert (len(finding) == 1)
    assert ("keystonemiddleware" in finding[0]["name"])


def test_multiple_filter_found():
    di = DistroInfo('minimal.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    pkgs = info['packages']

    rexen = {"project": "nova", "maintainers": "sven@redhat.com"}
    finding = query.filter_pkgs(pkgs, rexen)

    # expected number of foung pkgs is 2
    assert (isinstance(finding, list))
    assert (len(finding) == 2)


def test_filter_pkgs_not_found():
    di = DistroInfo('minimal.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    pkgs = info['packages']

    rexen = {"project": "nosuchproject", "tags": "newton"}
    finding = query.filter_pkgs(pkgs, rexen)

    # no package should be found
    assert (isinstance(finding, list))
    assert (len(finding) == 0)


def test_exclusion_filter_found():
    di = DistroInfo('minimal.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    pkgs = info['packages']
    rexen = {"tags": "~newton"}

    finding = query.filter_pkgs(pkgs, rexen)

    assert (finding)
    assert (isinstance(finding, list))
    assert (len(finding) == 1)
    assert ("newton" not in finding[0]["tags"])
