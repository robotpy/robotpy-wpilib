
import wpilib

from wpilib import SmartDashboard
from wpilib.buttons import JoystickButton

from commands.collect import Collect
from commands.drive_forward import DriveForward
from commands.low_goal import LowGoal
from commands.set_collection_speed import SetCollectionSpeed
from commands.set_pivot_setpoint import SetPivotSetpoint
from commands.shoot import Shoot

from subsystems.collector import Collector
from subsystems.pivot import Pivot

from triggers.double_button import DoubleButton


class OI(object):
    """
    The operator interface of the robot, it has been simplified from the real
    robot to allow control with a single PS3 joystick. As a result, not all
    functionality from the real robot is available.
    """

    def __init__(self, robot):
        self.joystick = wpilib.Joystick(0)

        JoystickButton(self.joystick, 12).whenPressed(LowGoal(robot))
        JoystickButton(self.joystick, 10).whenPressed(Collect(robot))

        JoystickButton(self.joystick, 11).whenPressed(SetPivotSetpoint(robot, Pivot.SHOOT))
        JoystickButton(self.joystick, 9).whenPressed(SetPivotSetpoint(robot, Pivot.SHOOT_NEAR))

        DoubleButton(self.joystick, 2, 3).whenActive(Shoot(robot))

        #SmartDashboard Buttons
        SmartDashboard.putData("Drive Forward", DriveForward(robot,2.25))
        SmartDashboard.putData("Drive Backward", DriveForward(robot,-2.25))
        SmartDashboard.putData("Start Rollers", SetCollectionSpeed(robot,Collector.FORWARD))
        SmartDashboard.putData("Stop Rollers", SetCollectionSpeed(robot,Collector.STOP))
        SmartDashboard.putData("Reverse Rollers", SetCollectionSpeed(robot,Collector.REVERSE))

    def getJoystick(self):
        return self.joystick
