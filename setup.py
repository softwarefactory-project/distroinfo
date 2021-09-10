#!/usr/bin/env python

import re
import setuptools
import sys

# In python < 2.7.4, a lazy loading of package `pbr` will break
# setuptools if some other modules registered functions in `atexit`.
# solution from: http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing  # noqa
except ImportError:
    pass


# Only require pytest_runner for setup when testing. This uses the
# recommendation from
# https://pypi.org/project/pytest-runner/#conditional-requirement
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setuptools.setup(
    setup_requires=['pbr'] + pytest_runner,
    tests_require=['pytest'],
    pbr=True)
