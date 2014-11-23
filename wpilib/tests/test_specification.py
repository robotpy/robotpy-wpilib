from tests import spec_scanner


def test_compare_file_specs(wpilib):
    path = "/home/christian/PycharmProjects/wpilib/wpilibj/wpilibJavaDevices/src/main/java/edu/wpi/first/wpilibj"
    output = spec_scanner.scan_specifications(wpilib, [path])
    for item in output:
        assert item["correct"]
