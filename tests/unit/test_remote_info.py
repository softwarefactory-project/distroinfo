from distroinfo.info import DistroInfo
from distroinfo.query import get_package

import tests.test_common as common



def test_remote_info():
    di = DistroInfo('remote.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()
    edf = info['package-default'].get('extra-default-field')
    assert edf == 'foo-default'
    nova = get_package(info, 'openstack-nova')
    assert nova['distgit'] == 'wololo'

