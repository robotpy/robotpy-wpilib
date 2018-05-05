'''
    This is the core of WPILib.
'''

import importlib
import sys

from ._impl.main import run

try:
    from .version import __version__
except ImportError:
    __version__ = 'master'


class WPILibLazyLoader:
    # TODO: use module __getattr__ when we drop support for Python < 3.7

    # Re-export things that Python expects at module level that are rarely used.
    __doc__ = __doc__
    __file__ = __file__
    __loader__ = __loader__
    __spec__ = __spec__

    __version__ = __version__

    def __init__(self):
        self._impl = _impl  # noqa: F821
        self.run = run

        # Re-export things used by the Python import machinery.
        self.__name__ = __name__
        self.__package__ = __package__
        self.__path__ = __path__

    def __getattr__(self, name):
        if not name[0].isupper():
            raise AttributeError("module 'wpilib' has no attribute {!r}".format(name))
        mod = importlib.import_module('.' + name.lower(), 'wpilib')
        cls = getattr(mod, name)
        setattr(self, name, cls)
        return cls


sys.modules['wpilib'] = WPILibLazyLoader()
