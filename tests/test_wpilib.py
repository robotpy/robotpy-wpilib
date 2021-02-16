import wpilib
import weakref


def test_sendable_chooser():
    chooser = wpilib.SendableChooser()
    assert chooser.getSelected() is None

    chooser.setDefaultOption("option", True)
    assert chooser.getSelected() is True


def test_smart_dashboard_putdata():
    t = wpilib.Talon(4)
    ref = weakref.ref(t)
    wpilib.SmartDashboard.putData("talon", t)
    del t
    assert bool(ref) is True
    assert wpilib.SmartDashboard.getData("talon") is ref()
