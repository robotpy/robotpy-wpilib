import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="function")
def timer(wpilib):
    return wpilib.Timer()


def test_timer_getFPGATimestamp(wpilib, sim_hooks):
    sim_hooks.time = 3.23
    assert wpilib.Timer.getFPGATimestamp() == pytest.approx(3.23, 0.01)


def test_timer_getMatchTime(wpilib):
    timer = wpilib.Timer()

    ds_impl = MagicMock()
    ds_impl.getMatchTime.return_value = 4.44
    wpilib.driverstation.DriverStation.instance = ds_impl
    assert wpilib.Timer.getMatchTime() == pytest.approx(4.44, 0.01)
    del wpilib.driverstation.DriverStation.instance


def test_timer_delay(wpilib, sim_hooks):
    sim_hooks.time = 10.0

    wpilib.Timer.delay(4.0)

    assert sim_hooks.time == pytest.approx(14.0, 0.01)


def test_timer_init(wpilib, sim_hooks):
    sim_hooks.time = 2.22
    timer = wpilib.Timer()

    assert timer.startTime == pytest.approx(2220.0, 0.01)


def test_timer_start(timer, sim_hooks):
    sim_hooks.time = 5.0
    timer.start()
    assert timer.startTime == pytest.approx(5000.0, 0.01)
    assert timer.get() == pytest.approx(0.0, 0.01)


def test_timer_get(timer, sim_hooks):
    sim_hooks.time = 5.0
    timer.start()
    sim_hooks.time = 7.0
    assert timer.get() == pytest.approx(2.0, 0.01)


def test_timer_reset(timer, sim_hooks):
    sim_hooks.time = 5.0
    timer.start()

    sim_hooks.time = 7.0
    timer.reset()
    assert timer.startTime == pytest.approx(7000.0, 0.01)
    assert timer.get() == pytest.approx(0.0, 0.01)


def test_timer_stop(timer, sim_hooks):
    sim_hooks.time = 5.0
    timer.start()

    sim_hooks.time = 7.0
    assert timer.get() == pytest.approx(2.0, 0.01)

    timer.stop()
    sim_hooks.time = 10.0
    assert timer.get() == pytest.approx(2.0, 0.01)


def test_timer_hasPeriodPassed(timer, sim_hooks):
    sim_hooks.time = 5.0
    timer.start()

    sim_hooks.time = 7.0
    assert timer.hasPeriodPassed(3.0) == False
    assert timer.get() == pytest.approx(2.0, 0.01)

    sim_hooks.time = 8.0
    assert timer.get() == pytest.approx(3.0, 0.01)
    assert timer.hasPeriodPassed(3.0) == False

    sim_hooks.time = 8.1
    assert timer.get() == pytest.approx(3.1, 0.01)

    assert timer.hasPeriodPassed(3.0) == True
    assert timer.startTime == pytest.approx(8000.0, 0.01)
    assert timer.get() == pytest.approx(0.1, 0.01)

    sim_hooks.time = 14.1
    assert timer.get() == pytest.approx(6.1, 0.01)

    # eh?
    assert timer.hasPeriodPassed(3.0) == True
    assert timer.startTime == pytest.approx(11000.0, 0.01)
    assert timer.get() == pytest.approx(3.1, 0.01)
