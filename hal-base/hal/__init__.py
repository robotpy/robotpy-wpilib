from .functions import *

try:
    from .version import __version__
except ImportError:
    __version__ = "master"

# Always initialize HAL, otherwise segfaults can happen
initialize()
