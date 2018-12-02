import pytest


@pytest.mark.parametrize("port", range(6))
def test_joystick(wpilib, hal_data, port):
    """
        Just some basic tests for the joystick
    """
    print(wpilib.__file__)
    data = hal_data["joysticks"][port]

    ds = wpilib.DriverStation.getInstance()
    j = wpilib.XboxController(port)
    left = wpilib.interfaces.GenericHID.Hand.kLeft
    right = wpilib.interfaces.GenericHID.Hand.kRight

    # X axis left
    data["axes"][0] = 0.5
    ds._getData()
    assert j.getX(left) == 0.5

    data["axes"][0] = -0.5
    ds._getData()
    assert j.getX(left) == -0.5

    # X axis right
    data["axes"][4] = 0.5
    ds._getData()
    assert j.getX(right) == 0.5

    data["axes"][4] = -0.5
    ds._getData()
    assert j.getX(right) == -0.5

    # Y axis
    data["axes"][1] = 0.5
    ds._getData()
    assert j.getY(left) == 0.5

    data["axes"][1] = -0.5
    ds._getData()
    assert j.getY(left) == -0.5

    # Y axis
    data["axes"][5] = 0.5
    ds._getData()
    assert j.getY(right) == 0.5

    data["axes"][5] = -0.5
    ds._getData()
    assert j.getY(right) == -0.5

    # Trigger Axis Left
    data["axes"][2] = 0.5
    ds._getData()
    assert j.getTriggerAxis(left) == 0.5

    data["axes"][2] = -0.5
    ds._getData()
    assert j.getTriggerAxis(left) == -0.5

    # Trigger Axis Right
    data["axes"][3] = 0.5
    ds._getData()
    assert j.getTriggerAxis(right) == 0.5

    data["axes"][3] = -0.5
    ds._getData()
    assert j.getTriggerAxis(right) == -0.5

    # Bumper
    data["buttons"][5] = True
    ds._getData()
    assert j.getBumper(left) == True

    data["buttons"][5] = False
    ds._getData()
    assert j.getBumper(left) == False

    # Bumper
    data["buttons"][6] = True
    ds._getData()
    assert j.getBumper(right) == True

    data["buttons"][6] = False
    ds._getData()
    assert j.getBumper(right) == False

    # Stick Left
    data["buttons"][9] = True
    ds._getData()
    assert j.getStickButton(left) == True

    data["buttons"][9] = False
    ds._getData()
    assert j.getStickButton(left) == False

    # Stick Right
    data["buttons"][10] = True
    ds._getData()
    assert j.getStickButton(right) == True

    data["buttons"][10] = False
    ds._getData()
    assert j.getStickButton(right) == False

    # Buttons
    for i in range(1, 12):
        data["buttons"][i] = True
        ds._getData()
        assert j.getRawButton(i) == True

        data["buttons"][i] = False
        ds._getData()
        assert j.getRawButton(i) == False

    # Rumble
    j.setRumble(wpilib.interfaces.GenericHID.RumbleType.kLeftRumble, 0.5)
    assert data["leftRumble"] == 32767

    j.setRumble(wpilib.interfaces.GenericHID.RumbleType.kLeftRumble, -0.5)
    assert data["leftRumble"] == 0

    # Rumble
    j.setRumble(wpilib.interfaces.GenericHID.RumbleType.kRightRumble, 0.5)
    assert data["rightRumble"] == 32767

    j.setRumble(wpilib.interfaces.GenericHID.RumbleType.kRightRumble, -0.5)
    assert data["rightRumble"] == 0

    # Name
    data["name"] = "Foo%s" % port
    assert j.getName() == data["name"]
