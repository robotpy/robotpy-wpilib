#!/usr/bin/env python3
'''
/*----------------------------------------------------------------------------*/
/* Copyright (c) FIRST 2008. All Rights Reserved.                             */
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*----------------------------------------------------------------------------*/
'''

import wpilib
from wpilib.command import Scheduler

from oi import OI

from commands.autonomous import Autonomous

from subsystems.claw import Claw
from subsystems.drivetrain import DriveTrain
from subsystems.elevator import Elevator
from subsystems.wrist import Wrist

class MyRobot(wpilib.IterativeRobot):

    def robotInit(self):
        '''This function is run when the robot is first started up and should be
           used for any initialization code.'''
        
        self.drivetrain = DriveTrain(self)
        self.elevator = Elevator(self)
        self.wrist = Wrist(self)
        self.claw = Claw()
        self.oi = OI(self)

        # instantiate the command used for the autonomous period
        self.autonomousCommand = Autonomous(self)
       
        # Show what command your subsystem is running on the SmartDashboard
        wpilib.SmartDashboard.putData(self.drivetrain)
        wpilib.SmartDashboard.putData(self.elevator)
        wpilib.SmartDashboard.putData(self.wrist)
        wpilib.SmartDashboard.putData(self.claw)

    def autonomousInit(self):
        # schedule the autonomous command (example)
        self.autonomousCommand.start()

    def autonomousPeriodic(self):
        '''This function is called periodically during autonomous'''
        Scheduler.getInstance().run()
        self.log()

    def teleopInit(self):
        # This makes sure that the autonomous stops running when
        # teleop starts running. If you want the autonomous to 
        # continue until interrupted by another command, remove
        # this line or comment it out.
        self.autonomousCommand.cancel()

    def teleopPeriodic(self):
        '''This function is called periodically during operator control'''
        Scheduler.getInstance().run()
        self.log()

    def testPeriodic(self):
        '''This function is called periodically during test mode'''
        wpilib.LiveWindow.run()

    def log(self):
        '''The log method puts interesting information to the SmartDashboard.'''
        self.wrist.log()
        self.elevator.log()
        self.drivetrain.log()
        self.claw.log()


if __name__ == '__main__':
    wpilib.run(MyRobot)
