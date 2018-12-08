import pytest
from unittest.mock import MagicMock, call


@pytest.fixture(scope="function")
def acc(wpilib):
    return wpilib.BuiltInAccelerometer()


@pytest.fixture(scope="function")
def acc_data(hal_data):
    return hal_data["accelerometer"]


@pytest.mark.parametrize("range", ["k2G", "k4G", "k8G"])
def test_bacc_setRange(wpilib, range, acc, acc_data):
    range = getattr(wpilib.BuiltInAccelerometer.Range, range)
    acc.setRange(range)
    assert acc_data["range"] == range


def test_bacc_setRange_invalid(wpilib, acc_data):
    with pytest.raises(ValueError):
        _ = wpilib.BuiltInAccelerometer(range=wpilib.BuiltInAccelerometer.Range.k16G)

    assert acc_data["active"] == False


def test_bacc_getX(acc, acc_data):
    acc_data["x"] = 3.14
    assert acc.getX() == 3.14


def test_bacc_getY(acc, acc_data):
    acc_data["y"] = 3.14
    assert acc.getY() == 3.14


def test_bacc_getZ(acc, acc_data):
    acc_data["z"] = 3.14
    assert acc.getZ() == 3.14


def test_bacc_initSendable(acc, sendablebuilder, acc_data):
    acc_data["x"] = 1
    acc_data["y"] = 2
    acc_data["z"] = 3

    acc.initSendable(sendablebuilder)
    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getValue("X", 0.0) == 1
    assert sendablebuilder.getTable().getValue("Y", 0.0) == 2
    assert sendablebuilder.getTable().getValue("Z", 0.0) == 3
