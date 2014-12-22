#!/usr/bin/env python3

import wpilib
from wpilib.command import Scheduler

from oi import OI

from commands.drive_and_shoot_autonomous import DriveAndShootAutonomous
from commands.drive_forward import DriveForward

from subsystems.collector import Collector
from subsystems.drivetrain import DriveTrain
from subsystems.pivot import Pivot
from subsystems.pneumatics import Pneumatics
from subsystems.shooter import Shooter




class Robot(wpilib.IterativeRobot):
    """This is the main class for running the PacGoat code."""
    
    def robotInit(self):
        """
        This function is run when the robot is first started up and should be
        used for any initialization code.
        """

        # Initialize the subsystems
        self.drivetrain = DriveTrain(self)
        self.collector = Collector(self)
        self.shooter = Shooter(self)
        self.pneumatics = Pneumatics(self)
        self.pivot = Pivot(self)
        wpilib.SmartDashboard.putData(self.drivetrain)
        wpilib.SmartDashboard.putData(self.collector)
        wpilib.SmartDashboard.putData(self.shooter)
        wpilib.SmartDashboard.putData(self.pneumatics)
        wpilib.SmartDashboard.putData(self.pivot)

        # This MUST be here. If the OI creates Commands (which it very likely
        # will), constructing it during the construction of CommandBase (from
        # which commands extend), subsystems are not guaranteed to be
        # yet. Thus, their requires() statements may grab null pointers. Bad
        # news. Don't move it.
        self.oi = OI(self)

        #instantiate the command used for the autonomous period
        self.autoChooser = wpilib.SendableChooser()
        self.autoChooser.addDefault("Drive and Shoot", DriveAndShootAutonomous(self))
        self.autoChooser.addObject("Drive Forward", DriveForward(self))
        wpilib.SmartDashboard.putData("Auto Mode", self.autoChooser)
        
        self.autonomousCommand = None

        # Pressurize the pneumatics
        self.pneumatics.start()

    def autonomousInit(self):
        self.autonomousCommand = self.autoChooser.getSelected()
        self.autonomousCommand.start()

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
        if self.autonomousCommand is not None:
            self.autonomousCommand.cancel()

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        Scheduler.getInstance().run()
        self.log()

    def testPeriodic(self):
        """This function is called periodically during test mode."""
        wpilib.LiveWindow.run()

    def disabledInit(self):
        self.shooter.unlatch()

    def disabledPeriodic(self):
        """This function is called periodically while disabled."""
        self.log()

    def log(self):
        self.pneumatics.writePressure()
        wpilib.SmartDashboard.putNumber("Pivot Pot Value", self.pivot.getAngle())
        wpilib.SmartDashboard.putNumber("Left Distance", self.drivetrain.getLeftEncoder().getDistance())
        wpilib.SmartDashboard.putNumber("Right Distance", self.drivetrain.getRightEncoder().getDistance())

if __name__ == "__main__":
    wpilib.run(Robot)
