#!/usr/bin/env python3
'''
    This is a demo program showing how to use Mecanum control with the
    RobotDrive class.
'''

import wpilib
from wpilib import RobotDrive

class MyRobot(wpilib.SampleRobot):
    
    # Channels for the wheels
    frontLeftChannel    = 2
    rearLeftChannel     = 3
    frontRightChannel   = 1
    rearRightChannel    = 0
    
    # The channel on the driver station that the joystick is connected to
    joystickChannel     = 0;

    def robotInit(self):
        '''Robot initialization function'''
        
        self.robotDrive = wpilib.RobotDrive(self.frontLeftChannel,
                                            self.rearLeftChannel,
                                            self.frontRightChannel,
                                            self.rearRightChannel)
        
        self.robotDrive.setExpiration(0.1)
        
        # invert the left side motors
        self.robotDrive.setInvertedMotor(RobotDrive.MotorType.kFrontLeft, True)
        
        # you may need to change or remove this to match your robot
        self.robotDrive.setInvertedMotor(RobotDrive.MotorType.kRearLeft, True)        

        self.stick = wpilib.Joystick(self.joystickChannel)
    
    def operatorControl(self):
        '''Runs the motors with Mecanum drive.'''
        
        self.robotDrive.setSafetyEnabled(True)
        while self.isOperatorControl() and self.isEnabled():
            
            # Use the joystick X axis for lateral movement, Y axis for forward movement, and Z axis for rotation.
            # This sample does not use field-oriented drive, so the gyro input is set to zero.
            self.robotDrive.mecanumDrive_Cartesian(self.stick.getX(),
                                                   self.stick.getY(),
                                                   self.stick.getZ(), 0);
            
            wpilib.Timer.delay(0.005)   # wait 5ms to avoid hogging CPU cycles

if __name__ == '__main__':
    wpilib.run(MyRobot)

