
import pytest

#
# Module-specific fixtures
#

@pytest.fixture(scope="function")
def servo(wpilib):
    return wpilib.Servo(2)

@pytest.fixture(scope="function")
def servo_data(hal_data):
    return hal_data['pwm'][2]

#
# Tests
#

@pytest.mark.parametrize("param,expected",
    [(-2.0, 0), (0.5, 0.5), (2.0, 1.0)])
def test_servo_position(param, expected, servo, servo_data):
    servo.set(param)
    assert servo_data['value'] == expected
    assert servo.get() == expected

@pytest.mark.parametrize("param,expected,expectedAngle",
    [(-90, 0, 0), (90, 0.5, 90), (200, 1.0, 180)])
def test_servo_angle(param, expected, expectedAngle, servo, servo_data):
    servo.setAngle(param)
    assert servo_data['value'] == expected
    assert servo.get() == expected
    assert servo.getAngle() == expectedAngle
