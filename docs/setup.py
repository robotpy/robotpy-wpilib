# this is a dirty hack to convince readthedocs to install a specific
# version of our software. We assume that this will always be triggered
# on a specific version

from setuptools import setup

try:
    from setuptools_scm import get_version
except ImportError:
    import subprocess

    def get_version(*args, **kwargs):
        return subprocess.check_output(["git", "describe", "--tags"], encoding="utf-8")


package = "wpilib"
version = get_version(root="..", relative_to=__file__)

setup(
    name="dummy-package",
    version="1.0",
    install_requires=["%s==%s" % (package, version)],
)
