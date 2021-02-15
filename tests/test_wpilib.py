import wpilib


def test_sendable_chooser():
    chooser = wpilib.SendableChooser()
    assert chooser.getSelected() is None

    chooser.setDefaultOption("option", True)
    assert chooser.getSelected() is True
