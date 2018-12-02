# For robot code
__halplatform__ = "sim"
__hal_simulation__ = True

try:
    from .version import __version__
except ImportError:
    __version__ = "master"
