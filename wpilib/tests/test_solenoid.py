import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def doublesolenoid(wpilib):
    return wpilib.DoubleSolenoid(0, 1)


@pytest.fixture(scope="function")
def doublesolenoid_table(networktables):
    return networktables.NetworkTables.getTable(
        "/LiveWindow/Ungrouped/DoubleSolenoid[0,0]"
    )


@pytest.fixture(scope="function")
def solenoid(wpilib):
    return wpilib.Solenoid(4)


@pytest.fixture(scope="function")
def solenoid_table(networktables):
    return networktables.NetworkTables.getTable("/LiveWindow/Ungrouped/Solenoid[0,4]")


def test_doublesolenoid_set(wpilib, hal, hal_data):

    ds = wpilib.DoubleSolenoid(0, 1)

    with pytest.raises(hal.exceptions.HALError):
        wpilib.Solenoid(1)

    assert ds.get() == ds.Value.kOff

    ds.set(ds.Value.kForward)
    assert ds.get() == ds.Value.kForward
    assert hal_data["solenoid"][0]["value"] == True
    assert hal_data["solenoid"][1]["value"] == False

    ds.set(ds.Value.kOff)
    assert ds.get() == ds.Value.kOff
    assert hal_data["solenoid"][0]["value"] == False
    assert hal_data["solenoid"][1]["value"] == False

    ds.set(ds.Value.kReverse)
    assert ds.get() == ds.Value.kReverse
    assert hal_data["solenoid"][0]["value"] == False
    assert hal_data["solenoid"][1]["value"] == True

    ds.close()

    ds = wpilib.DoubleSolenoid(0, 1)


def test_doublesolenoid_blacklisted(doublesolenoid):
    # ?hal?
    assert doublesolenoid.isFwdSolenoidBlackListed() == False
    assert doublesolenoid.isRevSolenoidBlackListed() == False


@pytest.mark.parametrize(
    "value_name, expected_output",
    [("kReverse", "Reverse"), ("kForward", "Forward"), ("kOff", "Off")],
)
def test_doublesolenoid_initSendable_update(
    doublesolenoid, sendablebuilder, value_name, expected_output
):
    doublesolenoid.set(getattr(doublesolenoid.Value, value_name))

    doublesolenoid.initSendable(sendablebuilder)
    prop = sendablebuilder.properties[0]
    assert prop.key == "Value"

    sendablebuilder.updateTable()
    assert sendablebuilder.getTable().getString("Value", "") == expected_output


@pytest.mark.parametrize(
    "input, expected_value_name",
    [("Reverse", "kReverse"), ("Forward", "kForward"), ("Off", "kOff")],
)
def test_doublesolenoid_initSendable_setter(
    doublesolenoid, sendablebuilder, input, expected_value_name
):
    doublesolenoid.initSendable(sendablebuilder)
    prop = sendablebuilder.properties[0]
    prop.setter(input)
    assert doublesolenoid.get() == getattr(doublesolenoid.Value, expected_value_name)


def test_solenoid(wpilib, hal, hal_data):

    for i in range(wpilib.SensorUtil.kSolenoidChannels):

        # ensure that it can be freed and allocated again
        for _ in range(2):
            s = wpilib.Solenoid(i)

            with pytest.raises(hal.exceptions.HALError):
                wpilib.Solenoid(i)

            assert hal_data["solenoid"][i]["initialized"]

            for v in [True, False, True, True, False]:
                s.set(v)
                assert hal_data["solenoid"][i]["value"] == v

                nv = not v
                hal_data["solenoid"][i]["value"] = nv
                assert s.get() == nv

            s.close()

            with pytest.raises(hal.HALError):
                s.set(True)


def test_multiple_solenoids(wpilib, hal_data):

    assert not hal_data["solenoid"][4]["initialized"]
    assert not hal_data["solenoid"][2]["initialized"]

    s1 = wpilib.Solenoid(4)
    assert hal_data["solenoid"][4]["initialized"]

    s2 = wpilib.Solenoid(2)
    assert hal_data["solenoid"][2]["initialized"]

    for i, s in [(4, s1), (2, s2)]:
        for v in [True, False, True, True, False]:
            s.set(v)
            assert hal_data["solenoid"][i]["value"] == v

            nv = not v
            hal_data["solenoid"][i]["value"] = nv
            assert s.get() == nv


def test_solenoid_isblacklisted(solenoid):
    # ?hal?
    assert solenoid.isBlackListed() == False


def test_solenoid_pulseduration(solenoid):
    solenoid.setPulseDuration(0.5)


def test_solenoid_startpulse(solenoid):
    # ?hal?
    # solenoid.startPulse()
    pass


def test_solenoid_initSendable_update(solenoid, sendablebuilder, hal_data):

    solenoid.initSendable(sendablebuilder)
    prop = sendablebuilder.properties[0]

    assert sendablebuilder.isActuator()
    assert prop.key == "Value"
    hal_data["solenoid"][4]["value"] = True
    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getBoolean("Value", False) == True


@pytest.mark.parametrize("value", [(True), (False)])
def test_solenoid_initSendable_setter(solenoid, sendablebuilder, hal_data, value):
    solenoid.initSendable(sendablebuilder)

    prop = sendablebuilder.properties[0]
    prop.setter(value)
    assert hal_data["solenoid"][4]["value"] == value


@pytest.mark.parametrize("value", [(1,), (0,), ([],)])
def test_solenoid_initSendable_setter_invalid(hal, solenoid, sendablebuilder, value):
    solenoid.initSendable(sendablebuilder)
    prop = sendablebuilder.properties[0]

    with pytest.raises(hal.HALError):
        prop.setter(value)


def test_solenoid_initSendable_safe(solenoid, sendablebuilder, hal_data):
    hal_data["solenoid"][4]["value"] == True
    solenoid.initSendable(sendablebuilder)
    sendablebuilder.startLiveWindowMode()

    assert hal_data["solenoid"][4]["value"] == False


def test_solenoidbase_getAll(wpilib, hal_data):

    solenoid = wpilib.SolenoidBase(0)

    for s in hal_data["solenoid"]:
        s["value"] = False

    assert solenoid.getAll() == 0

    for s in hal_data["solenoid"]:
        s["value"] = True

    assert solenoid.getAll() == 0xFF
    assert wpilib.SolenoidBase.getAll(0) == 0xFF

    hal_data["solenoid"][0]["value"] = False

    assert solenoid.getAll() == 0xFE
    assert wpilib.SolenoidBase.getAll(0) == 0xFE


def test_pcm_mapping(wpilib, hal_data):
    assert hal_data["solenoid"] is hal_data["pcm"][0]


def test_multiple_pcm(wpilib, hal_data):

    s0_1 = wpilib.Solenoid(0, 1)
    s1_1 = wpilib.Solenoid(1, 1)

    hal_data["pcm"][0][1]["value"] = True
    hal_data["pcm"][1][1]["value"] = False
    assert s0_1.get() == True
    assert s1_1.get() == False

    hal_data["pcm"][0][1]["value"] = False
    hal_data["pcm"][1][1]["value"] = True
    assert s0_1.get() == False
    assert s1_1.get() == True
