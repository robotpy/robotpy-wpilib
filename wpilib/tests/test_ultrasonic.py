import pytest
from unittest.mock import MagicMock, call


@pytest.fixture(scope="function")
def ultrasonic(wpilib):
    return wpilib.Ultrasonic(1, 2)


def test_ultrasonic_ctor(wpilib, hal_data):
    u = wpilib.Ultrasonic(1, 2)

    assert hal_data["dio"][1]["initialized"] == True
    assert hal_data["dio"][1]["is_input"] == False
    assert hal_data["dio"][2]["initialized"] == True
    assert hal_data["dio"][2]["is_input"] == True


def test_ultrasonic_auto(ultrasonic, hal_data):
    # This used to fail
    ultrasonic.setAutomaticMode(True)
    ultrasonic.setAutomaticMode(False)
    ultrasonic.setAutomaticMode(True)

    assert ultrasonic.isEnabled() == True
    ultrasonic.setEnabled(False)
    assert ultrasonic.isEnabled() == False
    ultrasonic.setEnabled(True)

    ultrasonic.setAutomaticMode(False)

    ultrasonic.ping()

    assert ultrasonic.isRangeValid() == False
    hal_data["counter"][0]["count"] = 5
    assert ultrasonic.isRangeValid() == True

    ultrasonic.close()


def test_ultrasonic_ping(ultrasonic, wpilib, hal_data):
    ultrasonic.ping()
    assert hal_data["dio"][1]["pulse_length"] == pytest.approx(
        wpilib.Ultrasonic.kPingTime, 0.01
    )

    assert ultrasonic.isRangeValid() == False
    hal_data["counter"][0]["count"] = 5  # wat? should be 2?
    assert ultrasonic.isRangeValid() == True

    ultrasonic.close()


def test_ultrasonic_getrange(ultrasonic, hal_data):
    ultrasonic.ping()
    hal_data["counter"][0]["count"] = 2
    hal_data["counter"][0]["period"] = 0.0012
    assert ultrasonic.getRangeInches() == pytest.approx(8.13, 0.01)
    assert ultrasonic.getRangeMM() == pytest.approx(206.5, 0.01)


def test_ultrasonic_pidsourcetype_allowed(ultrasonic, wpilib, hal_data):
    ultrasonic.setPIDSourceType(wpilib.interfaces.PIDSource.PIDSourceType.kDisplacement)
    assert (
        ultrasonic.getPIDSourceType()
        == wpilib.interfaces.PIDSource.PIDSourceType.kDisplacement
    )


def test_ultrasonic_pidsourcetype_notallowed(ultrasonic, wpilib):
    with pytest.raises(ValueError) as ex:
        ultrasonic.setPIDSourceType(wpilib.interfaces.PIDSource.PIDSourceType.kRate)


@pytest.mark.parametrize(
    "unit_name, expected_output", [("kInches", 8.13), ("kMillimeters", 206.5)]
)
def test_ultrasonic_pidget(ultrasonic, wpilib, hal_data, unit_name, expected_output):
    ultrasonic.ping()
    hal_data["counter"][0]["count"] = 2
    hal_data["counter"][0]["period"] = 0.0012
    unit = getattr(wpilib.Ultrasonic.Unit, unit_name)
    ultrasonic.setDistanceUnits(unit)
    assert ultrasonic.getDistanceUnits() == unit
    assert ultrasonic.pidGet() == pytest.approx(expected_output, 0.01)


def test_ultrasonic_pidget_invalid(ultrasonic):
    with pytest.raises(ValueError) as ex:
        ultrasonic.setDistanceUnits(-1)


def test_ultrasonic_initSendable1(ultrasonic, sendablebuilder, hal_data):
    ultrasonic.initSendable(sendablebuilder)

    assert sendablebuilder.getTable().getString(".type", None) == "Ultrasonic"
    assert not sendablebuilder.isActuator()

    ultrasonic.ping()
    hal_data["counter"][0]["count"] = 2
    hal_data["counter"][0]["period"] = 0.0012

    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getNumber("Value", 0) == pytest.approx(8.13, 0.01)
