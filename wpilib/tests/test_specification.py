
import os
from os.path import exists, join
import pytest


@pytest.mark.skipif(os.getenv('WPILIB_JAVA_DIR', None) == None,
                    reason="Must specify WPILIB_JAVA_DIR environment variable to run this test")
def test_check_wpilib_api(wpilib):

    from spec_scanners import wpilib_scanner

    wpilibj_dirs = wpilib_scanner.get_wpilib_dirs(os.environ['WPILIB_JAVA_DIR'])
    for tree in wpilibj_dirs:
        assert exists(tree), "WPILIB_JAVA_DIR does not point to wpilib tree dir"

    output = wpilib_scanner.compare_folders(wpilib, wpilibj_dirs)

    for item in output["children"]:
        if item["errors"] > 0:
            assert False, "Error: item {} doesn't match java spec, and is not ignored.".format(item["name"])


@pytest.mark.skipif(os.getenv('HAL_DIR', None) == None,
                    reason="Must specify HAL_DIR environment variable to run this test")
def test_check_hal_api(hal):

    from spec_scanners import hal_scanner

    hal_dirs = hal_scanner.get_hal_dirs(os.environ['HAL_DIR'])
    for tree in hal_dirs:
        assert exists(tree), "HAL_DIR does not point to hal tree dir"

    frontend_output = hal_scanner.compare_header_dirs(hal, hal_dirs)
    backend_output = hal_scanner.scan_c_end(hal, frontend_output)
    for item in backend_output["methods"]:
        if item["errors"] > 0:
            assert False, "Error: method call to {} doesn't match c++ spec.".format(item["name"])
    for item in backend_output["classes"]:
        if item["errors"] > 0:
            assert False, "Error: class {} doesn't match c++ spec, and is not ignored.".format(item["name"])