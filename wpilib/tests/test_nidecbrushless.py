import pytest
from unittest.mock import MagicMock, patch
from networktables import NetworkTables


@pytest.fixture(scope="function")
def nidec(wpilib):
    return wpilib.NidecBrushless(1, 2)


def test_nidec_init(wpilib, hal_data):
    motor = wpilib.NidecBrushless(1, 2)

    assert hal_data["pwm"][1]["initialized"]
    assert hal_data["dio"][2]["initialized"]
    assert not hal_data["dio"][2]["is_input"]


@pytest.mark.parametrize(
    "motor_input, expected_dio, inverted",
    [
        (-1.0, 1.00, True),
        (-1.0, 0.00, False),
        (-0.9, 0.95, True),
        (-0.9, 0.05, False),
        (-0.7, 0.85, True),
        (-0.7, 0.15, False),
        (-0.3, 0.65, True),
        (-0.3, 0.35, False),
        (0.0, 0.50, True),
        (0.0, 0.50, False),
        (0.3, 0.35, True),
        (0.3, 0.65, False),
        (0.7, 0.15, True),
        (0.7, 0.85, False),
        (0.9, 0.05, True),
        (0.9, 0.95, False),
        (1.0, 0.00, True),
        (1.0, 1.00, False),
    ],
)
def test_nidec_set(nidec, hal_data, motor_input, expected_dio, inverted):
    nidec.setInverted(inverted)

    nidec.set(motor_input)

    assert nidec.getInverted() == inverted
    assert nidec.get() == pytest.approx(motor_input, 0.01)

    assert hal_data["d0_pwm"][nidec.dio.pwmGenerator.pin][
        "duty_cycle"
    ] == pytest.approx(expected_dio, 0.01)


def test_nidec_expiration(nidec):
    nidec.setExpiration(111)

    assert nidec.getExpiration() == 111


def test_nidec_setSafetyEnabled1(nidec):
    nidec.stopMotor = MagicMock()

    nidec.setSafetyEnabled(True)

    nidec.set(0.5)

    nidec.check()
    nidec.stopMotor.assert_not_called()


def test_nidec_setSafetyEnabled2(nidec):
    nidec.stopMotor = MagicMock()

    nidec.setSafetyEnabled(True)

    # nidec.set(motor_input)

    nidec.check()
    assert not nidec.stopMotor.called


def test_nidec_isAlive1(nidec):
    nidec.setSafetyEnabled(False)

    assert nidec.isAlive()

    nidec.setSafetyEnabled(True)

    assert not nidec.isAlive()


def test_nidec_isAlive2(wpilib, sim_hooks):
    nidec = wpilib.NidecBrushless(1, 2)

    nidec.setSafetyEnabled(True)
    sim_hooks.time = 1.0

    assert not nidec.isAlive()

    nidec.feed()

    assert nidec.isAlive()


def test_nidec_disable(nidec, hal_data):
    nidec.disable()

    assert hal_data["d0_pwm"][nidec.dio.pwmGenerator.pin][
        "duty_cycle"
    ] == pytest.approx(0.5, 0.01)


def test_nidec_stopMotor(nidec, hal_data):
    nidec.stopMotor()

    assert hal_data["d0_pwm"][nidec.dio.pwmGenerator.pin][
        "duty_cycle"
    ] == pytest.approx(0.5, 0.01)


def test_nidec_getDescription(nidec):
    assert nidec.getDescription() == "Nidec 1"


def test_nidec_initSendable_update(nidec, sendablebuilder):
    nidec.set(0.5)
    nidec.initSendable(sendablebuilder)

    assert sendablebuilder.properties[0].key == "Value"

    sendablebuilder.updateTable()
    assert sendablebuilder.getTable().getNumber("Value", 0.0) == pytest.approx(0.5)


def test_nidec_initSendable_setter(nidec, sendablebuilder):
    nidec.initSendable(sendablebuilder)

    sendablebuilder.properties[0].setter(0.6)
    assert nidec.get() == 0.6


def test_nidec_initSendable_safe(nidec, sendablebuilder):
    nidec.stopMotor = MagicMock()
    nidec.initSendable(sendablebuilder)

    sendablebuilder.startLiveWindowMode()
    assert nidec.stopMotor.called
