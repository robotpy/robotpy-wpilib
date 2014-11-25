
import os
from os.path import exists, join
import pytest


@pytest.mark.skipif(os.getenv('WPILIB_JAVA_DIR', None) == None,
                    reason="Must specify WPILIB_JAVA_DIR environment variable to run this test")
def test_compare_file_specs(wpilib):


    path = os.environ['WPILIB_JAVA_DIR']
    path = join(path, 'wpilibJavaDevices', 'src', 'main', 'java', 'edu', 'wpi', 'first', 'wpilibj')
    assert exists(path), "WPILIB_JAVA_DIR does not point to wpilibj root dir"


    from . import java_scanner

    output = java_scanner.compare_folders(wpilib, [path])

    for item in output:
        if not item["matches"] and not item["ignored"]:
            print("Error: item {} doesn't match java spec, and is not ignored.".format(item["name"]))
            assert False
