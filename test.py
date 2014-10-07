#!/usr/bin/env python3
import wpilib

class MyRobot(wpilib.IterativeRobot):
    def robotInit(self):
        self.lstick = wpilib.Joystick(1)
        self.rstick = wpilib.Joystick(2)
        self.cstick = wpilib.Joystick(3)
        self.m1 = wpilib.Victor(1)
        self.m2 = wpilib.Victor(2)
        self.m3 = wpilib.Victor(3)
        self.drive = wpilib.RobotDrive(self.m1, self.m2)

    def teleopPeriodic(self):
        self.drive.tankDrive(self.lstick, self.rstick)
        self.m3.set(self.cstick.getY())

if __name__ == "__main__":
    wpilib.RobotBase.main(MyRobot)
