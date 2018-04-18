from distroinfo.info import DistroInfo

import tests.test_common as common


def test_rdoinfo_base():
    di = DistroInfo('rdo.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    common.assert_rdoinfo_base(info)


def test_rdoinfo_full():
    di = DistroInfo('rdo-full.yml',
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    common.assert_rdoinfo_full(info)


def test_rdoinfo_merge():
    di = DistroInfo(['rdo.yml', 'deps.yml'],
                    local_info=common.get_test_info_path('rdoinfo'))
    info = di.get_info()
    common.assert_rdoinfo_full(info)
