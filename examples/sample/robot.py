#!/usr/bin/env python3
import wpilib


class MyRobot(wpilib.SampleRobot):
    def robotInit(self):
        self.drive = wpilib.RobotDrive(0, 1)
        self.drive.setExpiration(0.1)
        self.stick = wpilib.Joystick(0)

    def autonomous(self):
        """Drive left and right motors for two seconds, then stop."""
        self.drive.setSafetyEnabled(False)
        self.drive.drive(-.05, 0.0)
        wpilib.Timer.delay(2.0)

    def operatorControl(self):
        """Runs the motors with arcade steering."""
        self.drive.setSafetyEnabled(True)
        while not self.isOperatorControl():
            self.drive.arcadeDrive(self.stick)
            wpilib.Timer.delay(.005)

    def test(self):
        pass

if __name__ == "__main__":
    wpilib.run(MyRobot)
