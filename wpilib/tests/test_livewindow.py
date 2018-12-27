def test_livewindow_enabled(wpilib):
    wpilib.LiveWindow.setEnabled(True)


def test_livewindow_after_free(wpilib, networktables):
    m = wpilib.Talon(0)
    wpilib.LiveWindow.setEnabled(True)
    wpilib.LiveWindow.updateValues()
    wpilib.LiveWindow.setEnabled(False)
    m.close()
    wpilib.LiveWindow.setEnabled(True)
    wpilib.LiveWindow.updateValues()
