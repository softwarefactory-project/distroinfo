from distroinfo import exception
from distroinfo.info import DistroInfo
import pytest

import tests.test_common as common


def test_invalid_info_file():
    di = DistroInfo('wololo.yml',
                    local_info=common.get_test_info_path('broken'))
    with pytest.raises(IOError):
        info = di.get_info()


def test_invalid_import():
    di = DistroInfo('invalid-import.yml',
                    local_info=common.get_test_info_path('broken'))
    with pytest.raises(IOError):
        info = di.get_info()


def test_circular_import():
    di = DistroInfo('circle1.yml',
                    local_info=common.get_test_info_path('broken'))
    with pytest.raises(exception.CircularInfoInclude):
        info = di.get_info()


def test_self_import():
    di = DistroInfo('self.yml',
                    local_info=common.get_test_info_path('broken'))
    with pytest.raises(exception.CircularInfoInclude):
        info = di.get_info()
