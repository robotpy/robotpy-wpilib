# For robot code
__halplatform__ = "roboRIO"
__hal_simulation__ = False

try:
    from .version import __version__
except ImportError:
    __version__ = "master"
