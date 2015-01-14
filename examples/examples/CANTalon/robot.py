#!/usr/bin/env python3

import wpilib


class MyRobot(wpilib.SampleRobot):
    '''
        This is a short sample program demonstrating how to use the basic throttle
        mode of the new CAN Talon.
    '''

    def robotInit(self):
        self.motor = wpilib.CANTalon(1) # Initialize the CanTalonSRX on device 1.

    def operatorControl(self):
        '''Runs the motor'''

        while self.isOperatorControl() and self.isEnabled():
            # Set the motor's output to half power.
            # This takes a number from -1 (100% speed in reverse) to +1 (100%
            # speed going forward)
            self.motor.set(0.5)

            wpilib.Timer.delay(0.01)  # Note that the CANTalon only receives
                                      # updates every 10ms, so updating more
                                      # quickly would not gain you anything.

        self.motor.disable()

if __name__ == '__main__':
    wpilib.run(MyRobot)
