#!/usr/bin/env python3

import importlib.machinery
import os
from os.path import dirname, exists, join
import subprocess
import sys

from setuptools import setup

# Check to see if we're on a RoboRIO before potentially downloading anything
if (
    os.environ.get("FORCE_HAL_INSTALL") != "1"
    and not "sdist" in sys.argv
    and not "egg_info" in sys.argv
    and not exists("/etc/natinst/share/scs_imagemetadata.ini")
):
    raise RuntimeError(
        "This HAL should only be installed onto a RoboRIO. Perhaps try the `robotpy-hal-sim` package?"
    )

setup_dir = dirname(__file__)
git_dir = join(setup_dir, "..", ".git")
base_package = "hal_impl"
version_file = join(setup_dir, base_package, "version.py")
hal_distutils_file = join(setup_dir, base_package, "distutils.py")

hal_distutils = importlib.machinery.SourceFileLoader(
    "hal_distutils", hal_distutils_file
).load_module()

hal_base_files = ["libwpiHal.so"]
wpiutil_base_files = ["libwpiutil.so"]

hal_files = {
    join("linux", "athena", "shared", f): join(setup_dir, base_package, f)
    for f in hal_base_files
}

wpiutil_files = {
    join("linux", "athena", "shared", f): join(setup_dir, base_package, f)
    for f in wpiutil_base_files
}

libs = hal_base_files + wpiutil_base_files

__version__ = "master"
__hal_version__ = None
__wpiutil_version__ = None

# Read the version if it exists
if exists(version_file):
    with open(version_file, "r") as fp:
        exec(fp.read(), globals())

# Download the HAL if required
if (
    not all(map(exists, hal_files.values()))
    or __hal_version__ != hal_distutils.hal_version
):
    hal_distutils.extract_hal_libs(hal_files)

if (
    not all(map(exists, wpiutil_files.values()))
    or __wpiutil_version__ != hal_distutils.wpiutil_version
):
    hal_distutils.extract_wpiutil_libs(wpiutil_files)

# Automatically generate a version.py based on the git version
if exists(git_dir):
    p = subprocess.Popen(
        ["git", "describe", "--tags", "--long", "--dirty=-dirty"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = p.communicate()
    # Make sure the git version has at least one tag
    if err:
        print("Error: You need to create a tag for this repo to use the builder")
        sys.exit(1)

    # Convert git version to PEP440 compliant version
    # - Older versions of pip choke on local identifiers, so we can't include the git commit
    version, commits, local = out.decode("utf-8").rstrip().split("-", 2)
    if commits != "0" or "-dirty" in local:
        version = "%s.post0.dev%s" % (version, commits)
else:
    version = __version__

# Generate a new version.py if required
if (
    not exists(version_file)
    or __version__ != version
    or __hal_version__ != hal_distutils.hal_version
    or __wpiutil_version__ != hal_distutils.wpiutil_version
):
    with open(version_file, "w") as fp:
        fp.write(
            "# Autogenerated by setup.py\n"
            "__version__ = '{0}'\n"
            "__hal_version__ = '{1}'\n"
            "__wpiutil_version__ = '{2}'\n".format(
                version, hal_distutils.hal_version, hal_distutils.wpiutil_version
            )
        )


with open(join(setup_dir, "README.rst"), "r") as readme_file:
    long_description = readme_file.read()

if __name__ == "__main__":
    setup(
        name="robotpy-hal-roborio",
        version=version,
        description="WPILib HAL layer for roboRIO platform",
        long_description=long_description,
        author="Peter Johnson, Dustin Spicuzza",
        author_email="robotpy@googlegroups.com",
        url="https://github.com/robotpy",
        keywords="frc first robotics hal can",
        packages=["hal_impl"],
        package_data={"hal_impl": libs},
        install_requires="robotpy-hal-base==" + version,  # is this a bad idea?
        license="BSD License",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "License :: OSI Approved :: BSD License",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Topic :: Scientific/Engineering",
        ],
    )
