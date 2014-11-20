from wpilib.command import CommandGroup
import global_vars
from commands.close_claw import CloseClaw
from commands.wait_for_pressure import WaitForPressure
from commands.check_for_hot_goal import CheckForHotGoal
from commands.set_pivot_setpoint import SetPivotSetpoint
from commands.drive_forward import DriveForward
from commands.shoot import Shoot
#TODO Check this when done


class DriveAndShootAutonomous(CommandGroup):
    """
    Drive over the line and then shoot the ball. If the hot goal is not detected,
    it will wait briefly.
    """

    def __init__(self):
        self.addSequential(CloseClaw())
        self.addSequential(WaitForPressure(), 2)
        if global_vars.is_real():
            #NOTE: Simulation doesn't currently have the concept of hot.
            self.addSequential(CheckForHotGoal(2))
        self.addSequential(SetPivotSetpoint(45))
        self.addSequential(DriveForward(8, 0.3))
        self.addSequential(Shoot())
        super().__init__()
