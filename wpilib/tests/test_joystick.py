import pytest


@pytest.mark.parametrize("port", range(6))
def test_joystick(wpilib, hal_data, port):
    """
        Just some basic tests for the joystick
    """

    data = hal_data["joysticks"][port]

    ds = wpilib.DriverStation.getInstance()
    j = wpilib.Joystick(port)

    # X axis
    data["axes"][0] = 0.5
    ds._getData()
    assert j.getX() == 0.5

    data["axes"][0] = -0.5
    ds._getData()
    assert j.getX() == -0.5

    # Y axis
    data["axes"][1] = 0.5
    ds._getData()
    assert j.getY() == 0.5

    data["axes"][1] = -0.5
    ds._getData()
    assert j.getY() == -0.5

    # Trigger
    data["buttons"][1] = True
    ds._getData()
    assert j.getTrigger() == True

    data["buttons"][1] = False
    ds._getData()
    assert j.getTrigger() == False

    # Top
    data["buttons"][2] = True
    ds._getData()
    assert j.getTop() == True

    data["buttons"][2] = False
    ds._getData()
    assert j.getTop() == False

    # Buttons
    for i in range(1, 12):
        data["buttons"][i] = True
        ds._getData()
        assert j.getRawButton(i) == True

        data["buttons"][i] = False
        ds._getData()
        assert j.getRawButton(i) == False

    # Name
    data["name"] = "Foo%s" % port
    assert j.getName() == data["name"]
