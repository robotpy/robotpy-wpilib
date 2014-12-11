
import os
from os.path import exists, join
import pytest


@pytest.mark.skipif(os.getenv('WPILIB_JAVA_DIR', None) == None,
                    reason="Must specify WPILIB_JAVA_DIR environment variable to run this test")
def test_check_wpilib_api(wpilib):


    path = os.environ['WPILIB_JAVA_DIR']
    path = join(path, 'wpilibJavaDevices', 'src', 'main', 'java', 'edu', 'wpi', 'first', 'wpilibj')
    assert exists(path), "WPILIB_JAVA_DIR does not point to wpilibj root dir"

    from spec_scanners import wpilib_scanner

    output = wpilib_scanner.compare_folders(wpilib, [path])

    for item in output["children"]:
        if item["errors"] > 0:
            assert False, "Error: item {} doesn't match java spec, and is not ignored.".format(item["name"])


@pytest.mark.skipif(os.getenv('HAL_DIR', None) == None,
                    reason="Must specify HAL_DIR environment variable to run this test")
def test_check_hal_api(hal):


    path = os.environ['HAL_DIR']
    path = join(path, 'include', 'HAL')
    assert exists(path), "HAL_DIR does not point to HAL root dir"

    from spec_scanners import hal_scanner

    frontend_output = hal_scanner.compare_header_dirs(hal, [path])
    backend_output = hal_scanner.scan_c_end(hal, frontend_output)
    for item in backend_output["methods"]:
        if item["errors"] > 0:
            assert False, "Error: method call to {} doesn't match c++ spec.".format(item["name"])
    for item in backend_output["classes"]:
        if item["errors"] > 0:
            assert False, "Error: class {} doesn't match c++ spec, and is not ignored.".format(item["name"])