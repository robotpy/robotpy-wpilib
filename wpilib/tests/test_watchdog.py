import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture("function")
def MockThread():
    with patch("threading.Thread", new=MagicMock()) as Thread:
        yield Thread


def test_init2(wpilib, MockThread):
    cb = MagicMock()
    doggo = wpilib.Watchdog(2, cb)

    assert doggo._timeout == 2000000
    assert isinstance(doggo._timeout, int)
    assert doggo._callback is cb
    assert not doggo.isExpired()
