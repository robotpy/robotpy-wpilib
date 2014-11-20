#!/usr/bin/env python3
import wpilib
from wpilib.command import Scheduler
from commands.drive_and_shoot_autonomous import DriveAndShootAutonomous
from commands.drive_forward import DriveForward
from subsystems.collector import Collector
from subsystems.drivetrain import DriveTrain
from subsystems.pivot import Pivot
from subsystems.pneumatics import Pneumatics
from subsystems.Shooter import Shooter
from oi import Oi
import global_vars


class Robot(wpilib.IterativeRobot):
    """This is the main class for running the PacGoat code."""
    def robotInit(self):
        """
        This function is run when the robot is first started up and should be
        used for any initialization code.
        """

        #Initialize the subsystems
        global_vars.subsystems["drivetrain"] = DriveTrain()
        global_vars.subsystems["collector"] = Collector()
        global_vars.subsystems["shooter"] = Shooter()
        global_vars.subsystems["pneumatics"] = Pneumatics()
        global_vars.subsystems["pivot"] = Pivot()
        wpilib.SmartDashboard.putData(global_vars.subsystems["drivetrain"])
        wpilib.SmartDashboard.putData(global_vars.subsystems["collector"])
        wpilib.SmartDashboard.putData(global_vars.subsystems["shooter"])
        wpilib.SmartDashboard.putData(global_vars.subsystems["pneumatics"])
        wpilib.SmartDashboard.putData(global_vars.subsystems["pivot"])

        global_vars.oi = Oi()

        #instantiate the command used for the autonomous period
        self.auto_chooser = wpilib.SendableChooser()
        self.auto_chooser.addDefault("Drive and Shoot", DriveAndShootAutonomous())
        self.auto_chooser.addObject("Drive Forward", DriveForward())
        wpilib.SmartDashboard.putData("Auto Mode", self.auto_chooser)

        #Pressurize the pneumatics
        global_vars.subsystems["pneumatics"].start()

    def autonomousInit(self):
        self.autonomous_command = self.auto_chooser.getSelected()
        self.autonomous_command.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous"""
        Scheduler.getInstance().run()
        self.log()

    def teleopInit(self):
        """This function is called at the beginning of operator control."""
        #This makes sure that the autonomous stops running when
        #teleop starts running. If you want the autonomous to
        #continue until interrupted by another command, remove
        #this line or comment it out.
        if self.autonomous_command is not None:
            self.autonomous_command.cancel()

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        Scheduler.getInstance().run()
        self.log()

    def testPeriodic(self):
        """This function is called periodically during test mode."""
        wpilib.LiveWindow.run()

    def disabledInit(self):
        global_vars.subsystems["shooter"].unlatch()

    def disabledPeriodic(self):
        """This function is called periodically while disabled."""
        self.log()

    def log(self):
        global_vars.subsystems["shooter"].write_pressure()
        wpilib.SmartDashboard.putNumber("Pivot Pot Value", self.pivot.get_angle())
        wpilib.SmartDashboard.putNumber("Left Distance", self.drivetrain.get_left_encoder().getDistance())
        wpilib.SmartDashboard.putNumber("Right Distance", self.drivetrain.get_right_encoder().getDistance())


if __name__ == "__main__":
    global_vars.real = False
    wpilib.RobotBase.main(Robot)
