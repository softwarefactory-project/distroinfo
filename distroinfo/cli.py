import sys

import logging

from . import __version__
from distroinfo import shell


def distroinfo(*cargs):
    """
    distroinfo Command-Line Interface

    """
    return shell.run(cargs=cargs, version=__version__)


def main():
    """
    distroinfo console_scripts entry point
    """
    # setup logging to terminal
    logging.basicConfig(level=logging.DEBUG,
                        stream=sys.stdout)
    sh_log = logging.getLogger('sh')
    sh_log.setLevel(logging.WARN)
    cargs = sys.argv[1:]
    sys.exit(distroinfo(*cargs))


if __name__ == '__main__':
    main()
