import wpilib
from wpilib.buttons import JoystickButton
from .commands.collect import Collect
from .commands.drive_forward import DriveForward
from .commands.low_goal import LowGoal
from .commands.set_collection_speed import SetCollectionSpeed
from .commands.set_pivot_setpoint import SetPivotSetpoint
from .commands.shoot import Shoot
from .subsystems.collector import Collector
from .subsystems.pivot import Pivot
from .triggers.double_button import DoubleButton


class Oi(object):
    """
    The operator interface of the robot, it has been simplified from the real
    robot to allow control with a single PS3 joystick. As a result, not all
    functionality from the real robot is available.

    """

    def __init__(self):
        self.joystick = wpilib.Joystick(1)

        JoystickButton(self.joystick, 12).whenPressed(LowGoal())
        JoystickButton(self.joystick, 10).whenPressed(Collect())

        JoystickButton(self.joystick, 11).whenPressed(SetPivotSetpoint(Pivot.SHOOT))
        JoystickButton(self.joystick, 9).whenPressed(SetPivotSetpoint(Pivot.SHOOT_NEAR))

        DoubleButton(self.joystick, 2, 3).whenActive(Shoot())

        #SmartDashboard Buttons
        wpilib.SmartDashboard.putData("Drive Forward", DriveForward(2.25))
        wpilib.SmartDashboard.putData("Drive Backward", DriveForward(-2.25))
        wpilib.SmartDashboard.putData("Start Rollers", SetCollectionSpeed(Collector.FORWARD))
        wpilib.SmartDashboard.putData("Stop Rollers", SetCollectionSpeed(Collector.STOP))
        wpilib.SmartDashboard.putData("Reverse Rollers", SetCollectionSpeed(Collector.REVERSE))

    def get_joystick(self):
        return self.joystick
