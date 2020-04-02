distroinfo
==========

``distroinfo`` is a python module for parsing, validating and querying
distribution/packaging metadata stored in human readable and reviewable
text/YAML files.

This is a proper generic (re)implementation of
`rdoinfo <https://github.com/redhat-openstack/rdoinfo>`__ parser which
proved well suited for the task of interfacing with distribution
metadata in a human friendly way. If you consider code reviews human
friendly, that is.

``distroinfo`` is a part of `Software Factory
project <https://softwarefactory-project.io/docs/>`__

STATUS
------

``distroinfo`` is available from Fedora/EPEL repos and is **BEING
INTEGRATED**.

`rdopkg <https://github.com/softwarefactory-project/rdopkg>`__ and
`DLRN <https://github.com/softwarefactory-project/DLRN>`__ are first
adopters.

``rdoinfo`` compatibility is ensured through offline and online tests.

CI is enabled.

See `distroinfo
reviews <https://softwarefactory-project.io/dashboard/project_distroinfo>`__.

Use github
`Issues <https://github.com/softwarefactory-project/distroinfo/issues>`__
to make requests and report bugs.

Installation
------------

from source
~~~~~~~~~~~

If you want to hack ``distroinfo`` or just have the latest code without
waiting for next release, you can use the git repo directly:

::

    git clone https://github.com/softwarefactory-project/distroinfo
    cd distroinfo
    python setup.py develop --user

You may set the preference over ``distroinfo`` RPM by correctly
positioning ``~/.local/bin/distroinfo`` in your ``$PATH``.

Or you can use virtualenv to avoid conflicts with RPM:

::

    git clone https://github.com/softwarefactory-project/distroinfo
    cd distroinfo
    virtualenv --system-site-packages ~/distroinfo-venv
    source ~/distroinfo-venv/bin/activate
    python setup.py develop
    ln `which distroinfo` ~/bin/distroinfo-dev

    distroinfo-dev --version

Required python modules are listed in
`requirements.txt <requirements.txt>`__.

from Fedora/EPEL repos (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``distroinfo`` is available on **Fedora 27** and newer:

::

    dnf install python2-distroinfo

including Python 3 version:

::

    dnf install python3-distroinfo

On CentOS/RHEL 7, ``distroinfo`` is available from
`EPEL <https://fedoraproject.org/wiki/EPEL>`__.

On **CentOS 7**:

::

    yum install epel-release
    yum install python2-distroinfo

On **RHEL 7**:

::

    yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    yum install python2-distroinfo

from PyPI
~~~~~~~~~

For your convenience, ``distroinfo`` is available from the Cheese Shop:

::

    pip install distroinfo

Usage
-----

You can **fetch info files from an URL** by specifying ``remote_info``
base URL:

::

    from distroinfo.info import DistroInfo

    RDOINFO_RAW_URL = \
        'https://raw.githubusercontent.com/redhat-openstack/rdoinfo/master/'

    di = DistroInfo('rdo-full.yml',
                    remote_info=RDOINFO_RAW_URL)
    info = di.get_info()

Or you can **fetch info files from a remote git repository** using
``remote_git_info``:

::

    from distroinfo.info import DistroInfo

    RDOINFO_GIT_URL = \
        'https://github.com/redhat-openstack/rdoinfo'

    di = DistroInfo('rdo-full.yml',
                    remote_git_info=RDOINFO_GIT_URL)
    info = di.get_info()

Or you can **fetch info files from a local directory** using
``local_info``:

::

    from distroinfo.info import DistroInfo

    INFO_PATH = '/path/to/info'

    di = DistroInfo('rdo-full.yml',
                    local_info=INFO_PATH)
    info = di.get_info()

For remote fetchers info files/repos are cached in
``~/.distroinfo/cache``.

You can navigate info structure yourself or use ``query`` module:

::

    from distroinfo import query

    # get a package info by strict package name
    nova = query.get_package(info, 'openstack-nova')

    # find a package by human reference (smart search)
    keystone = query.find_package(info, 'keystone')

Alternatively, you can get info with ``packages`` and ``releases`` as
dictionaries indexed by project/release name for easier access using
``info_dicts=True``:

::

    info = di.get_info(info_dicts=True)
    nova = info['packages']['nova']

Until proper documentation is in place, please refer to:

-  `rdoinfo <https://github.com/redhat-openstack/rdoinfo>`__ for prime
   example of ``distroinfo`` format usage
-  `rdoinfo integration
   tests <https://github.com/softwarefactory-project/distroinfo/blob/master/tests/integration/test_rdoinfo_online.py>`__
   for code examples
-  `dlrn.drivers.rdoinfo <https://github.com/softwarefactory-project/DLRN/blob/master/dlrn/drivers/rdoinfo.py>`__
   for a real world code that uses tags and
   ``remote_git_info``/``local_info``
-  `distroinfo.info <https://github.com/softwarefactory-project/distroinfo/blob/master/distroinfo/info.py>`__
   to RTFS

Command Line Interface
----------------------

A simple CLI is provided in ``scripts/di.py`` which can be used to test
basic ``distroinfo`` functionality, profile, dump parsed data, etc.

An example of dumping parsed rdoinfo into both YAML and JSON files:

::

    $> ./scripts/di.py dump -y rdoinfo.yaml -j rdoinfo.json -f git \
           'https://github.com/redhat-openstack/rdoinfo' rdo-full.yml

    Dumping YAML to: rdoinfo.yaml
    Dumping JSON to: rdoinfo.json

Additional ``docopt`` module is required to run the CLI.

Bugs
----

Please use the `github
Issues <https://github.com/softwarefactory-project/distroinfo/issues>`__
to report bugs.
