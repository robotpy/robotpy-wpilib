#!/usr/bin/env python3
import wpilib

class MyRobot(wpilib.IterativeRobot):
    def robotInit(self):
        self.lstick = wpilib.Joystick(1)
        self.m1 = wpilib.Victor(1)

    def teleopPeriodic(self):
        self.m1.set(self.lstick.getY())

if __name__ == "__main__":
    wpilib.RobotBase.main(MyRobot)
