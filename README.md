# distroinfo

`distroinfo` is a python module for parsing, validating and querying
distribution/packaging metadata stored in human readable and reviewable
text/YAML files.

This is a proper generic (re)implementation of
[rdoinfo](https://github.com/redhat-openstack/rdoinfo) parser which proved
well suited for the task of interfacing with distribution metadata in a human
friendly way. If you consider code reviews human friendly, that is.

`distroinfo` is a part of
[Software Factory project](https://softwarefactory-project.io/docs/)


## STATUS

`distroinfo` is **READY FOR INTEGRATION**

[rdopkg](https://github.com/softwarefactory-project/rdopkg) and
[DLRN](https://github.com/softwarefactory-project/DLRN) are first adopters.

`rdoinfo` compatibility is ensured through offline and online tests.

CI is enabled.

Documentation and RPM packaging in progress.

See [distroinfo reviews](https://softwarefactory-project.io/dashboard/project_distroinfo).

Use github
[Issues](https://github.com/softwarefactory-project/distroinfo/issues)
to make requests and report bugs.

Poke `jruzicka` on `#softwarefactory` or `#rdo` Freenode IRC for more
information.


## Installation


### from source

If you want to hack `ditroinfo` or just have the latest code without waiting
for next release, you can use the git repo directly:

    git clone https://github.com/softwarefactory-project/distroinfo
    cd distroinfo
    python setup.py develop --user

You may set the preference over `distroinfo` RPM by correctly positioning
`~/.local/bin/distroinfo` in your `$PATH`.

Or you can use virtualenv to avoid conflicts with RPM:

    git clone https://github.com/softwarefactory-project/distroinfo
    cd distroinfo
    virtualenv --system-site-packages ~/distroinfo-venv
    source ~/distroinfo-venv/bin/activate
    python setup.py develop
    ln `which distroinfo` ~/bin/distroinfo-dev

    distroinfo-dev --version

Required python modules are listed in
[requirements.txt](requirements.txt).


### from Fedora/EPEL repos (default)

**TODO:** `distroinfo` is going to hit Fedora/EPEL repos as soon as it's
ready.


### from PyPI

For your convenience, `distroinfo` is available from the Cheese Shop:

    pip install distroinfo


## Usage

Until proper documentation is in place, please refer to:

* [rdoinfo](https://github.com/redhat-openstack/rdoinfo) for prime example of
  `distroinfo` format usage
* [rdoinfo integration tests](https://github.com/softwarefactory-project/distroinfo/blob/master/tests/integration/test_rdoinfo_online.py)
  for code examples
* [distroinfo.info](https://github.com/softwarefactory-project/distroinfo/blob/master/distroinfo/info.py)
  to RTFS


## Bugs

Please use the
[github Issues](https://github.com/softwarefactory-project/distroinfo/issues)
to report bugs.
