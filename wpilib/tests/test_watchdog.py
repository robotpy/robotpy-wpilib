import threading
import time

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture("function")
def MockThread():
    with patch("threading.Thread", new=MagicMock()) as Thread:
        yield Thread


class Counter:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.value = 0

    def __repr__(self) -> str:
        return "<Counter value=%r>" % self.value

    def get(self) -> int:
        with self.lock:
            return self.value

    def reset(self) -> None:
        with self.lock:
            self.value = 0

    def increment(self) -> None:
        with self.lock:
            self.value += 1


def test_init2(wpilib, MockThread):
    cb = MagicMock()
    doggo = wpilib.Watchdog(2, cb)

    assert doggo._timeout == 2000000
    assert isinstance(doggo._timeout, int)
    assert doggo._callback is cb
    assert not doggo.isExpired()


def test_enable_disable(wpilib):
    watchdog_counter = Counter()

    watchdog = wpilib.Watchdog(0.4, watchdog_counter.increment)

    # Run 1
    watchdog.enable()
    time.sleep(0.2)
    watchdog.disable()

    assert watchdog_counter.get() == 0, "Watchdog triggered early"

    # Run 2
    watchdog_counter.reset()
    watchdog.enable()
    time.sleep(0.6)
    watchdog.disable()

    assert watchdog_counter.get() == 1

    # Run 3
    watchdog_counter.reset()
    watchdog.enable()
    time.sleep(1)
    watchdog.disable()

    assert watchdog_counter.get() == 1


def test_reset(wpilib):
    watchdog_counter = Counter()

    watchdog = wpilib.Watchdog(0.4, watchdog_counter.increment)

    watchdog.enable()
    time.sleep(0.2)
    watchdog.reset()
    time.sleep(0.2)
    watchdog.disable()

    assert watchdog_counter.get() == 0, "Watchdog triggered early"


def test_setTimeout(wpilib):
    watchdog_counter = Counter()

    watchdog = wpilib.Watchdog(1, watchdog_counter.increment)

    watchdog.enable()
    time.sleep(0.2)
    watchdog.setTimeout(0.2)

    assert watchdog.getTimeout() == 0.2
    assert watchdog_counter.get() == 0, "Watchdog triggered early"

    time.sleep(0.3)
    watchdog.disable()

    assert watchdog_counter.get() == 1


def test_isExpired(wpilib):
    watchdog = wpilib.Watchdog(0.2, lambda: None)
    watchdog.enable()

    assert not watchdog.isExpired()
    time.sleep(0.3)
    assert watchdog.isExpired()


def test_epochs(wpilib):
    watchdog_counter = Counter()

    watchdog = wpilib.Watchdog(1, watchdog_counter.increment)

    # Run 1
    watchdog.enable()
    watchdog.addEpoch("Epoch 1")
    time.sleep(0.1)
    watchdog.addEpoch("Epoch 2")
    time.sleep(0.1)
    watchdog.addEpoch("Epoch 3")
    watchdog.disable()

    assert watchdog_counter.get() == 0, "Watchdog triggered early"

    # Run 2
    watchdog.enable()
    watchdog.addEpoch("Epoch 1")
    time.sleep(0.2)
    watchdog.reset()
    time.sleep(0.2)
    watchdog.addEpoch("Epoch 2")
    watchdog.disable()

    assert watchdog_counter.get() == 0, "Watchdog triggered early"


def test_multi_watchdog(wpilib):
    watchdog_counter1 = Counter()
    watchdog_counter2 = Counter()

    watchdog1 = wpilib.Watchdog(0.2, watchdog_counter1.increment)
    watchdog2 = wpilib.Watchdog(0.6, watchdog_counter2.increment)

    watchdog2.enable()
    time.sleep(0.2)

    assert watchdog_counter1.get() == 0, "Watchdog triggered early"
    assert watchdog_counter2.get() == 0, "Watchdog triggered early"

    # Sleep enough such that only the watchdog enabled later times out first
    watchdog1.enable()
    time.sleep(0.3)
    watchdog1.disable()
    watchdog2.disable()

    assert watchdog_counter1.get() == 1
    assert watchdog_counter2.get() == 0, "Watchdog triggered early"
