import pytest
from unittest.mock import MagicMock
import time


def test_motorsafety(wpilib):
    wpilib.RobotState.isDisabled = lambda: False
    wpilib.RobotState.isTest = lambda: False
    safety = wpilib.MotorSafety()
    safety.stopMotor = MagicMock()

    assert not safety.isSafetyEnabled()
    safety.getDescription = lambda: ""
    safety.setSafetyEnabled(True)
    assert safety.isSafetyEnabled()

    safety.setExpiration(0.2)
    safety.feed()
    assert safety.getExpiration() == 0.2
    assert safety.isAlive()
    safety.setExpiration(0.1)
    time.sleep(0.2)

    assert not safety.isAlive()
    safety.feed()
    assert safety.isAlive()
    time.sleep(0.2)
    safety.check()
    safety.stopMotor.assert_called_once_with()
