import pytest


def test_preferences(wpilib, hal_data):
    """
        Just some basic tests for the joystick
    """
    nt = wpilib.Preferences.getInstance()

    nt.putString("test1", "Hello")
    nt.putBoolean("test2", False)
    nt.putInt("test3", 5)
    nt.putFloat("test4", 0.5)

    wpilib.Preferences.instance = None
    del wpilib.Preferences.instance

    nt = wpilib.Preferences.getInstance()
    assert nt.getString("test1") == "Hello"
    assert nt.getBoolean("test2") == False
    assert nt.getInt("test3") == 5
    assert nt.getFloat("test4") == 0.5
