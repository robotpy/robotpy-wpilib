#!/usr/bin/env python3
'''
    This sample program shows how to control a motor using a joystick. In the
    operator control part of the program, the joystick is read and the value
    is written to the motor.

    Joystick analog values range from -1 to 1 and speed controller inputs also
    range from -1 to 1 making it easy to work together. The program also delays
    a short time in the loop to allow other threads to run. This is generally
    a good idea, especially since the joystick values are only transmitted
    from the Driver Station once every 20ms.
'''

import wpilib

class MyRobot(wpilib.SampleRobot):
    
    #: update every 0.005 seconds/5 milliseconds (200Hz)
    kUpdatePeriod = 0.005
    
    def robotInit(self):
        '''Robot initialization function'''
        
        self.motor = wpilib.Talon(0)        # initialize the motor as a Talon on channel 0
        self.stick = wpilib.Joystick(0)     # initialize the joystick on port 0
        
    def operatorControl(self):
        '''Runs the motor from a joystick.'''
        
        while self.isOperatorControl() and self.isEnabled():
            
            # Set the motor's output.
            # This takes a number from -1 (100% speed in reverse) to
            # +1 (100% speed going forward)
            
            self.motor.set(self.stick.getY())
            
            wpilib.Timer.delay(self.kUpdatePeriod)  # wait 5ms to the next update

if __name__ == "__main__":
    wpilib.run(MyRobot)
