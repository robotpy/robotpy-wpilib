from unittest.mock import MagicMock

import pytest


@pytest.fixture("function")
def acc(wpilib):
    aa = wpilib.AnalogAccelerometer(2)
    aa.analogChannel.getAverageVoltage = MagicMock(return_value=3)
    return aa


def test_init(wpilib):
    acc1 = wpilib.AnalogAccelerometer(0)
    assert acc1.allocatedChannel

    acc2 = wpilib.AnalogAccelerometer(wpilib.AnalogInput(1))
    assert not acc2.allocatedChannel


def test_getAcceleration(acc):
    assert acc.getAcceleration() == (3 - 2.5) / 1
    channel = acc.analogChannel
    acc.analogChannel = None
    assert acc.getAcceleration() == 0
    acc.analogChannel = channel


def test_setSensitivity(acc):
    acc.setSensitivity(2)
    assert acc.voltsPerG == 2


def test_setZero(acc):
    acc.setZero(0)
    assert acc.zeroGVoltage == 0
