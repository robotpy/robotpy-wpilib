def test_iterativerobot_printLoopOverrunMessage(wpilib):
    robot = wpilib.IterativeRobot()

    robot.printLoopOverrunMessage()


def test_timedrobot(wpilib):
    robot = wpilib.TimedRobot()

    assert robot.getPeriod() == 0.02


def test_timedrobot2(wpilib):
    robot = wpilib.TimedRobot(0.013)

    assert robot.getPeriod() == 0.013
