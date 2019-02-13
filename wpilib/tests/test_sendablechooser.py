def test_chooser_control(wpilib, networktables):
    """
        Integration test to ensure that we don't accidentally break
        the chooser control used by various testing infrastructure
    """

    import networktables.util

    k1 = object()
    k2 = object()

    chooser = wpilib.SendableChooser()
    chooser.addOption("k1", k1)
    chooser.setDefaultOption("k2", k2)

    assert chooser.getSelected() is k2

    wpilib.SmartDashboard.putData("testc", chooser)

    control = networktables.util.ChooserControl("testc")
    assert control.getSelected() == "k2"

    control.setSelected("k1")
    networktables.NetworkTables.waitForEntryListenerQueue(5)
    assert chooser.getSelected() is k1

    control.setSelected("kX")
    networktables.NetworkTables.waitForEntryListenerQueue(5)
    assert chooser.getSelected() is None
