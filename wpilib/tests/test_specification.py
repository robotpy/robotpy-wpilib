
import os
from os.path import exists, join
import pytest


@pytest.mark.skipif(os.getenv('WPILIB_JAVA_DIR', None) == None,
                    reason="Must specify WPILIB_JAVA_DIR environment variable to run this test")
def test_compare_java_specs_wpilib(wpilib):


    path = os.environ['WPILIB_JAVA_DIR']
    path = join(path, 'wpilibJavaDevices', 'src', 'main', 'java', 'edu', 'wpi', 'first', 'wpilibj')
    assert exists(path), "WPILIB_JAVA_DIR does not point to wpilibj root dir"

    from spec_scanners import java_scanner

    output = java_scanner.compare_folders(wpilib, [path])

    for item in output["children"]:
        if item["errors"] > 0:
            assert False, "Error: item {} doesn't match java spec, and is not ignored.".format(item["name"])


@pytest.mark.skipif(os.getenv('HAL_DIR', None) == None,
                    reason="Must specify HAL_DIR environment variable to run this test")
def test_compare_cpp_specs_hal(hal):


    path = os.environ['HAL_DIR']
    path = join(path, 'include', 'HAL')
    assert exists(path), "HAL_DIR does not point to HAL root dir"

    from spec_scanners import cpp_scanner

    output = cpp_scanner.compare_folders(hal, [path])

    for item in output["methods"]:
        if item["errors"] > 0:
            assert False, "Error: method {} doesn't match java spec, and is not ignored.".format(item["name"])
    for item in output["classes"]:
        if item["errors"] > 0:
            assert False, "Error: class {} doesn't match java spec, and is not ignored.".format(item["name"])