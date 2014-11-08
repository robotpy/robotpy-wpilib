# For robot code
__halplatform__ = 'roboRIO'

try:
    from .version import __version__
except ImportError:
    __version__ = 'master'
