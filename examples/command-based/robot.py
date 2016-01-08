
import wpilib
from wpilib import command

from subsystems.example_subsystem import ExampleSubsystem
from commands.example_command import ExampleCommand
from oi import OI


class MyRobot(wpilib.IterativeRobot):

    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        # Create operator interface
        self.oi = OI(self)
        # Create subsystems
        self.example_subsystem = ExampleSubsystem(self)
        #Create the command used for the autonomous period
        self.autonomous_command = ExampleCommand(self)

    def autonomousInit(self):
        #Schedule the autonomous command
        self.autonomous_command.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        command.Scheduler.getInstance().run()

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        command.Scheduler.getInstance().run()

    def testPeriodic(self):
        """This function is called periodically during test mode."""
        wpilib.LiveWindow.run()

if __name__ == "__main__":
    wpilib.run(MyRobot)
