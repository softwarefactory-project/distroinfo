from distroinfo.info import DistroInfo
from distroinfo.query import get_package
from distroinfo.query import get_release

import tests.test_common as common


def test_remote_info():
    di = DistroInfo('remote.yml',
                    local_info=common.get_test_info_path('minimal'))
    info = di.get_info()

    edf = info['package-default'].get('extra-default-field')
    assert edf == 'foo-default-%(project)s'

    nova = get_package(info, 'openstack-nova')
    assert nova['extra-default-field'] == 'foo-default-nova'
    assert nova['extra-conf-field'] == 'foo-conf-nova'
    assert nova['master-distgit'] == 'overriden-nova'
    assert 'extra@maintain.er' in nova['maintainers']

    rocky = get_release(info, 'rocky')
    assert rocky['branch'] == 'overriden-branch'
