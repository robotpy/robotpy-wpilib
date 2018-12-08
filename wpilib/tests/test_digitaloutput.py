import pytest


def test_digitaloutput_init(wpilib, hal_data):
    di = wpilib.DigitalOutput(2)
    assert hal_data["dio"][2]["initialized"]
    assert not hal_data["dio"][2]["is_input"]


def test_digitaloutput_get(wpilib, hal_data):
    di = wpilib.DigitalOutput(2)
    hal_data["dio"][2]["value"] = True
    assert di.get()


def test_digitaloutput_set(wpilib, hal_data):
    di = wpilib.DigitalOutput(2)

    di.set(True)
    assert hal_data["dio"][2]["value"] == True

    di.set(False)
    assert hal_data["dio"][2]["value"] == False


def test_digitaloutput_initSendable(wpilib, sendablebuilder, hal_data):
    hal_data["dio"][2]["value"] = True
    di = wpilib.DigitalOutput(2)

    di.initSendable(sendablebuilder)
    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getBoolean("Value", None) == True

    assert sendablebuilder.properties[0].key == "Value"
    sendablebuilder.properties[0].setter(False)
    assert hal_data["dio"][2]["value"] == False
