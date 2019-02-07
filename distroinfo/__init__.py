import pbr.version
import logging


logging.basicConfig(level=logging.WARNING)
logging.getLogger("distroinfo").setLevel(logging.WARNING)

version_info = pbr.version.VersionInfo('distroinfo')
try:
    __version__ = version_info.version_string()
except AttributeError:
    __version__ = None

__all__ = ['__version__']
