import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture('function')
def MockThread():
    with patch('threading.Thread', new=MagicMock()) as Thread:
        yield Thread


def test_init1(wpilib, sim_hooks, MockThread):
    sim_hooks.time = 4.5
    doggo = wpilib.Watchdog(2)

    assert doggo.timeout == 2
    assert doggo.callback is not None
    assert doggo.startTime == 4.5
    assert not doggo.isExpired()
    assert doggo.getTime() == 0


def test_init2(wpilib, sim_hooks, MockThread):
    sim_hooks.time = 4.5
    cb = MagicMock()
    doggo = wpilib.Watchdog(2, cb)

    assert doggo.timeout == 2
    assert doggo.callback == cb
    assert doggo.startTime == 4.5
    assert not doggo.isExpired()
    assert doggo.getTime() == 0

