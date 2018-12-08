import importlib.machinery
import io
import os
from os.path import abspath, dirname, exists, join
import shutil
import zipfile

import pytest

hal_dir = abspath(join(dirname(__file__), "__hal__"))
hal_version_file = join(hal_dir, "version")

hal_distutils_file = abspath(
    join(dirname(__file__), "..", "..", "hal-roborio", "hal_impl", "distutils.py")
)


def _download_hal_includes():

    hal_distutils = importlib.machinery.SourceFileLoader(
        "hal_setup_py", hal_distutils_file
    ).load_module()
    hal_version = hal_distutils.hal_version

    print("Using HAL", hal_distutils.hal_version)
    print()

    if exists(hal_dir):
        # find the version
        if exists(hal_version_file):
            with open(hal_version_file) as fp:
                if hal_version == fp.read().strip():
                    return

        # Nope, gotta download a new distribution
        shutil.rmtree(hal_dir)

    # Download the hal zipfile
    hal_distutils.extract_hal_headers(hal_dir)

    # write the version to a file
    with open(hal_version_file, "w") as fp:
        fp.write(hal_version + "\n")


def test_check_hal_api(hal):
    """
        This test checks the HAL API against the include files that our Jenkins
        buildbot zips up when it builds our HAL shared library. If they don't
        match, then it may result in memory corruption or segfaults.
        
        This test ensures that the HAL shared library can be downloaded, and 
        also checks our HAL against the one that we claim to be compiled against.
    """

    _download_hal_includes()

    from spec_scanners.hal_scanner import (
        Class,
        collect_headers,
        compare,
        get_hal_dirs,
        print_outputs,
    )

    hal_dirs = get_hal_dirs(hal_dir)
    for tree in hal_dirs:
        assert exists(tree), "Invalid HAL include directory"

    c_data = collect_headers(hal_dirs)

    py_data = Class.from_py("hal", hal)

    outputs, num_errors, _, _ = compare(c_data, py_data, True)

    if num_errors > 0:
        outputs = [o for o in outputs if o.errors]
        print_outputs(outputs, errors_only=True)

        assert False, "Check stdout for failure details"


@pytest.mark.skipif(
    os.getenv("WPILIB_JAVA_DIR", None) == None,
    reason="Must specify WPILIB_JAVA_DIR environment variable to run this test",
)
def test_check_wpilib_api(wpilib):
    """
        These just check to see if our implementation is in line with
        the WPILib implementation. Not critical.
    """

    from spec_scanners import wpilib_scanner

    wpilibj_dirs = wpilib_scanner.get_wpilib_dirs(os.environ["WPILIB_JAVA_DIR"])
    for tree in wpilibj_dirs:
        assert exists(tree), "WPILIB_JAVA_DIR does not point to wpilib tree dir"

    output = wpilib_scanner.compare_folders(wpilib, wpilibj_dirs)

    for item in output["children"]:
        if item["errors"] > 0:
            assert (
                False
            ), "Error: item {} doesn't match java spec, and is not ignored.".format(
                item["name"]
            )
