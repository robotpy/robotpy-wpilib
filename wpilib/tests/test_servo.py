import pytest
from unittest.mock import MagicMock

#
# Module-specific fixtures
#

@pytest.fixture(scope="function")
def servo(wpilib):
    return wpilib.Servo(2)

@pytest.fixture(scope="function")
def servo_data(hal_data):
    return hal_data['pwm'][2]


@pytest.fixture(scope="function")
def servo_table(networktables):
    return networktables.NetworkTables.getTable("/LiveWindow/Ungrouped/Servo[2]")

#
# Tests
#

def test_servo_ctor(servo, servo_data):
    assert servo_data['initialized'] == True


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


def test_servo_getservoanglerange(servo):
    assert servo.getServoAngleRange() == pytest.approx(180, 0.01)


def test_servo_initTable(servo, servo_table, hal_data):
    servo.set(0.5)

    servo.initTable(servo_table)

    assert servo_table.getNumber("Value", 0.0) == pytest.approx(0.5, 0.01)


def test_servo_initTable_null(servo, hal_data):
    servo.initTable(None)
    assert servo.valueEntry is None
    assert servo.valueListener is None


def test_servo_valueChanged(servo):
    servo.set = MagicMock()
    servo.valueChanged(None, None, 0.5, None)

    servo.set.assert_called_once_with(0.5)


def test_servo_livewindowmode(servo, servo_table, hal_data):
    servo.initTable(servo_table)

    servo.startLiveWindowMode()

    assert servo.valueListener is not None

    servo.stopLiveWindowMode()

    assert servo.valueListener is None
