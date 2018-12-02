import pytest
from unittest.mock import MagicMock


def test_init_speedgroupcontroller(wpimock, halmock):
    halmock.getFPGATime.return_value = 1000
    halmock.getLoopTiming.return_value = (
        wpimock.SensorUtil.kSystemClockTicksPerMicrosecond
    )

    m1 = MagicMock()
    m2 = MagicMock()

    assert wpimock.SpeedControllerGroup.instances == 0
    group = wpimock.SpeedControllerGroup(m1, m2)
    assert wpimock.SpeedControllerGroup.instances == 1
    assert m1, m2 in group.speedControllers


@pytest.fixture(scope="function")
def speed_group(wpimock, halmock):
    halmock.getFPGATime.return_value = 1000

    m1 = MagicMock()
    m1.set = MagicMock()
    m1.disable = MagicMock()
    m1.stopMotor = MagicMock()
    m1.pidWrite = MagicMock()

    m2 = MagicMock()
    m2.set = MagicMock()
    m2.disable = MagicMock()
    m2.stopMotor = MagicMock()
    m2.pidWrite = MagicMock()

    m3 = MagicMock()
    m3.set = MagicMock()
    m3.disable = MagicMock()
    m3.stopMotor = MagicMock()
    m3.pidWrite = MagicMock()

    group = wpimock.SpeedControllerGroup(m1, m2, m3)
    return group


def test_set(speed_group):
    speed_group.set(1)
    for controller in speed_group.speedControllers:
        controller.set.assert_called_once_with(1)


def test_inverted(speed_group):
    speed_group.setInverted(True)
    assert speed_group.getInverted()
    for controller in speed_group.speedControllers:
        controller.set(1)
        controller.set.assert_called_once_with(1)
        controller.set.reset_mock()

    speed_group.set(1)
    for controller in speed_group.speedControllers:
        controller.set.assert_called_once_with(-1)


def test_disable(speed_group):
    speed_group.disable()
    for controller in speed_group.speedControllers:
        controller.disable.assert_called_once_with()


def test_stopmotor(speed_group):
    speed_group.stopMotor()
    for controller in speed_group.speedControllers:
        controller.stopMotor.assert_called_once_with()


def test_pidwrite(speed_group):
    speed_group.pidWrite(1)
    for controller in speed_group.speedControllers:
        controller.pidWrite.asser_called_once_with()
