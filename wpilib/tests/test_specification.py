
import os
from os.path import exists, join
import pytest


@pytest.mark.skipif(os.getenv('WPILIB_JAVA_DIR', None) == None,
                    reason="Must specify WPILIB_JAVA_DIR environment variable to run this test")
def test_compare_file_specs(wpilib):


    path = os.environ['WPILIB_JAVA_DIR']
    path = join(path, 'wpilibJavaDevices', 'src', 'main', 'java', 'edu', 'wpi', 'first', 'wpilibj')
    assert exists(path), "WPILIB_JAVA_DIR does not point to wpilibj root dir"


    import spec_scanner

    output = spec_scanner.scan_specifications(wpilib, [path])

    for item in output:
        assert item["matches"] or item["ignored"]
