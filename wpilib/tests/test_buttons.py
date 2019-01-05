def test_JoystickButton_whenPressed(wpilib, hal_data, enable_robot):
    ds = wpilib.DriverStation.getInstance()
    joystick = wpilib.Joystick(1)
    data = hal_data["joysticks"][1]
    button = wpilib.buttons.JoystickButton(joystick, 1)

    command = wpilib.command.Command()
    button.whenPressed(command)

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    scheduler = wpilib.command.Scheduler.getInstance()

    scheduler.run()

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()
    assert command.isRunning()
    scheduler.run()
    assert command.isRunning()

    data["buttons"][1] = False
    ds._getData()
    assert joystick.getRawButton(1) == False
    scheduler.run()

    # command keeps running
    assert command.isRunning()


def test_JoystickButton_whileHeld(wpilib, hal_data):
    ds = wpilib.DriverStation.getInstance()
    joystick = wpilib.Joystick(1)
    data = hal_data["joysticks"][1]
    button = wpilib.buttons.JoystickButton(joystick, 1)

    command = wpilib.command.Command()
    button.whileHeld(command)

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    scheduler = wpilib.command.Scheduler.getInstance()

    scheduler.run()

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()
    assert command.isRunning()
    scheduler.run()
    assert command.isRunning()

    data["buttons"][1] = False
    ds._getData()
    assert joystick.getRawButton(1) == False
    scheduler.run()

    # command stops
    assert not command.isRunning()


def test_JoystickButton_whenReleased(wpilib, hal_data, enable_robot):
    ds = wpilib.DriverStation.getInstance()
    joystick = wpilib.Joystick(1)
    data = hal_data["joysticks"][1]
    button = wpilib.buttons.JoystickButton(joystick, 1)

    command = wpilib.command.Command()
    button.whenReleased(command)

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    scheduler = wpilib.command.Scheduler.getInstance()

    scheduler.run()

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()
    assert not command.isRunning()
    scheduler.run()
    assert not command.isRunning()

    data["buttons"][1] = False
    ds._getData()
    assert joystick.getRawButton(1) == False
    scheduler.run()

    # command starts
    assert command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()

    # command continues
    assert command.isRunning()


def test_JoystickButton_toggleWhenPressed(wpilib, hal_data, enable_robot):
    ds = wpilib.DriverStation.getInstance()
    joystick = wpilib.Joystick(1)
    data = hal_data["joysticks"][1]
    button = wpilib.buttons.JoystickButton(joystick, 1)

    command = wpilib.command.Command()
    button.toggleWhenPressed(command)

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    scheduler = wpilib.command.Scheduler.getInstance()

    scheduler.run()

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()

    # command starts
    assert command.isRunning()
    scheduler.run()
    assert command.isRunning()

    data["buttons"][1] = False
    ds._getData()
    assert joystick.getRawButton(1) == False
    scheduler.run()

    assert command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()

    # command stops
    assert not command.isRunning()


def test_JoystickButton_cancelWhenPressed(wpilib, hal_data):
    ds = wpilib.DriverStation.getInstance()
    joystick = wpilib.Joystick(1)
    data = hal_data["joysticks"][1]
    button = wpilib.buttons.JoystickButton(joystick, 1)

    command = wpilib.command.Command()
    button.cancelWhenPressed(command)

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    scheduler = wpilib.command.Scheduler.getInstance()

    scheduler.run()

    assert joystick.getRawButton(1) == False
    assert not command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()

    # command starts
    assert not command.isRunning()
    scheduler.run()
    assert not command.isRunning()

    data["buttons"][1] = False
    ds._getData()
    assert joystick.getRawButton(1) == False
    scheduler.run()

    assert not command.isRunning()
    command.start()
    scheduler.run()
    assert command.isRunning()

    data["buttons"][1] = True
    ds._getData()
    assert joystick.getRawButton(1) == True
    scheduler.run()

    # command stops
    assert not command.isRunning()
