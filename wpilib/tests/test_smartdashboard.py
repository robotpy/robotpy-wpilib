import pytest


def test_smartdashboard_basic(networktables, wpilib):

    ntsd = networktables.NetworkTables.getTable("SmartDashboard")

    sd = wpilib.SmartDashboard

    ntsd.putBoolean("bool", True)
    assert sd.getBoolean("bool", None) == True

    sd.putNumber("number", 1)
    assert ntsd.getNumber("number", None) == 1

    assert sd.getString("string", None) == None

    ntsd.putString("string", "s")
    assert sd.getString("string", None) == "s"


def test_smartdashboard_getSelected(wpilib, sendablebuilder):
    o1 = object()
    o2 = object()
    o3 = object()

    chooser = wpilib.SendableChooser()
    chooser.addOption("o1", o1)
    chooser.addOption("o2", o2)
    chooser.setDefaultOption("o3", o3)
    chooser.initSendable(sendablebuilder)

    # Default should work
    assert chooser.getSelected() == o3

    wpilib.SmartDashboard.putData("Autonomous Mode", chooser)
    # Default should still work
    assert chooser.getSelected() == o3
    # switch it up
    sendablebuilder.properties.__getitem__(3).setter("o1")
    # New choice should now be returned
    assert chooser.getSelected() == o1


def test_smartdashboard_getSelected_nodefault(wpilib, sendablebuilder):

    o1 = object()
    o2 = object()

    chooser = wpilib.SendableChooser()
    chooser.addObject("o1", o1)
    chooser.addObject("o2", o2)
    chooser.initSendable(sendablebuilder)

    assert chooser.getSelected() is None

    # switch it up
    ct = sendablebuilder.getTable()
    ct.putString(chooser.SELECTED, "o1")
    sendablebuilder.properties.__getitem__(3).setter("o1")

    # New choice should now be returned
    assert chooser.getSelected() == o1


def test_smartdashboard_updateValues(wpilib):
    wpilib.SmartDashboard.updateValues()
