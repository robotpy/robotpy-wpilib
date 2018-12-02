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
    return hal_data["pwm"][2]


@pytest.fixture(scope="function")
def servo_table(networktables):
    return networktables.NetworkTables.getTable("/LiveWindow/Ungrouped/Servo[2]")


#
# Tests
#


def test_servo_ctor(servo, servo_data):
    assert servo_data["initialized"] == True


@pytest.mark.parametrize("param,expected", [(-2.0, 0), (0.5, 0.5), (2.0, 1.0)])
def test_servo_position(param, expected, servo, servo_data):
    servo.set(param)
    assert servo_data["value"] == expected
    assert servo.get() == expected


@pytest.mark.parametrize(
    "param,expected,expectedAngle", [(-90, 0, 0), (90, 0.5, 90), (200, 1.0, 180)]
)
def test_servo_angle(param, expected, expectedAngle, servo, servo_data):
    servo.setAngle(param)
    assert servo_data["value"] == expected
    assert servo.get() == expected
    assert servo.getAngle() == expectedAngle


def test_servo_getServoAngleRange(servo):
    assert servo.getServoAngleRange() == pytest.approx(180.0, 0.01)


def test_servo_initSendable(servo, sendablebuilder):
    servo.set(0.5)
    servo.initSendable(sendablebuilder)

    assert sendablebuilder.properties[0].key == "Value"

    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getNumber("Value", 0.0) == pytest.approx(0.5)

    sendablebuilder.properties[0].setter(2.0)
    assert servo.get() == pytest.approx(1.0)
