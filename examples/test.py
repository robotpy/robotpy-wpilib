#!/usr/bin/env python3
import wpilib

class MyRobot(wpilib.IterativeRobot):
    def robotInit(self):
        self.lstick = wpilib.Joystick(0)
        self.rstick = wpilib.Joystick(1)
        self.cstick = wpilib.Joystick(2)
        self.m1 = wpilib.Victor(0)
        self.m2 = wpilib.Victor(1)
        self.m3 = wpilib.Victor(2)
        self.drive = wpilib.RobotDrive(self.m1, self.m2)
        self.shifter = wpilib.DoubleSolenoid(0, 1)

    def teleopPeriodic(self):
        self.drive.tankDrive(self.lstick, self.rstick)
        self.m3.set(self.cstick.getY())
        if self.lstick.getTrigger():
            self.shifter.set(wpilib.DoubleSolenoid.Value.kForward)
        if self.rstick.getTrigger():
            self.shifter.set(wpilib.DoubleSolenoid.Value.kReverse)

if __name__ == "__main__":
    wpilib.run(MyRobot)
