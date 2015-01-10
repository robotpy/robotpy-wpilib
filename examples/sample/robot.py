#!/usr/bin/env python3
'''
    This is a demo program showing the use of the RobotDrive class.
    
    The SampleRobot class is the base of a robot application that will
    automatically call your Autonomous and OperatorControl methods at
    the right time as controlled by the switches on the driver station
    or the field controls.
    
    WARNING: While it may look like a good choice to use for your code
    if you're inexperienced, don't. Unless you know what you are doing,
    complex code will be much more difficult under this system. Use
    IterativeRobot or Command-Based instead if you're new.
'''

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
        
        while self.isOperatorControl() and self.isEnabled():
            self.drive.arcadeDrive(self.stick)  # drive with arcade style (use right stick)
            wpilib.Timer.delay(.005)    # wait for a motor update time

    def test(self):
        '''Runs during test mode'''
        pass

if __name__ == "__main__":
    wpilib.run(MyRobot)
