
from wpilib.command import CommandGroup

from commands.close_claw import CloseClaw
from commands.wait_for_pressure import WaitForPressure
from commands.check_for_hot_goal import CheckForHotGoal
from commands.set_pivot_setpoint import SetPivotSetpoint
from commands.drive_forward import DriveForward
from commands.shoot import Shoot


class DriveAndShootAutonomous(CommandGroup):
    """
    Drive over the line and then shoot the ball. If the hot goal is not detected,
    it will wait briefly.
    """

    def __init__(self, robot):
        super().__init__()
        self.addSequential(CloseClaw(robot))
        self.addSequential(WaitForPressure(robot), 2)
        if robot.isReal():
            # NOTE: Simulation doesn't currently have the concept of hot.
            self.addSequential(CheckForHotGoal(robot, 2))
        self.addSequential(SetPivotSetpoint(robot, 45))
        self.addSequential(DriveForward(robot, 8, 0.3))
        self.addSequential(Shoot(robot))
