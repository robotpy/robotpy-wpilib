#!/usr/bin/env python3

import wpilib

class MyRobot(wpilib.SampleRobot):
    '''This is a demo program showing how to use Gyro control with the
    RobotDrive class.'''
    
    def robotInit(self):
        '''Robot initialization function'''
        gyroChannel = 0 #analog input
        
        self.joystickChannel = 0 #usb number in DriverStation
    
        #channels for motors
        self.leftMotorChannel = 1
        self.rightMotorChannel = 0
        self.leftRearMotorChannel = 3
        self.rightRearMotorChannel = 2
    
        self.angleSetpoint = 0.0
        self.pGain = 1 #propotional turning constant
    
        #gyro calibration constant, may need to be adjusted 
        #gyro value of 360 is set to correspond to one full revolution
        self.voltsPerDegreePerSecond = .0128
              
        self.myRobot = wpilib.RobotDrive(wpilib.CANTalon(self.leftMotorChannel), 
                                         wpilib.CANTalon(self.leftRearMotorChannel), 
                                         wpilib.CANTalon(self.rightMotorChannel), 
                                         wpilib.CANTalon(self.rightRearMotorChannel))
        
        self.gyro = wpilib.AnalogGyro(gyroChannel)
        self.joystick = wpilib.Joystick(self.joystickChannel)
    
    def autonomous(self):
        '''Runs during Autonomous'''
        pass

   
    def operatorControl(self):
        '''
        Sets the gyro sensitivity and drives the robot when the joystick is pushed. The
        motor speed is set from the joystick while the RobotDrive turning value is assigned
        from the error between the setpoint and the gyro angle.
        '''
        
        self.gyro.setSensitivity(self.voltsPerDegreePerSecond) #calibrates gyro values to equal degrees
        while self.isOperatorControl() and self.isEnabled():
            turningValue =  (self.angleSetpoint - self.gyro.getAngle())*self.pGain
            if self.joystick.getY() <= 0:
                #forwards
                self.myRobot.drive(self.joystick.getY(), turningValue)
            elif self.joystick.getY() > 0:
                #backwards
                self.myRobot.drive(self.joystick.getY(), -turningValue)
            wpilib.Timer.delay(0.005)
            
    def test(self):
        '''Runs during test mode'''
        pass
    
if __name__ == "__main__":
    wpilib.run(MyRobot)