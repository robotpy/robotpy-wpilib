#!/usr/bin/env python3

"""
    Copied from https://github.com/CrossTheRoadElec/FRC-Examples/blob/master/JAVA_VelocityClosedLoop/src/org/usfirst/frc/team469/robot/Robot.java
    
    Example demonstrating the velocity closed-loop servo.
    Tested with Logitech F350 USB Gamepad inserted into Driver Station
    
    Be sure to select the correct feedback sensor using SetFeedbackDevice() below.
    
    After deploying/debugging this to your RIO, first use the left Y-stick
    to throttle the Talon manually.  This will confirm your hardware setup.
    Be sure to confirm that when the Talon is driving forward (green) the
    position sensor is moving in a positive direction.  If this is not the cause
    flip the boolena input to the SetSensorDirection() call below.
    
    Once you've ensured your feedback device is in-phase with the motor,
    use the button shortcuts to servo to target velocity.
    
    Tweak the PID gains accordingly.
"""

import wpilib

class MyRobot(wpilib.IterativeRobot):
      
    def robotInit(self):
        
        self.talon = wpilib.CANTalon(7)
        self.joy = wpilib.Joystick(0)
        self.loops = 0
                             
        # first choose the sensor
        self.talon.setFeedbackDevice(wpilib.CANTalon.FeedbackDevice.CtreMagEncoder_Relative)
        self.talon.reverseSensor(False)
        #self.talon.configEncoderCodesPerRev(XXX), // if using FeedbackDevice.QuadEncoder
        #self.talon.configPotentiometerTurns(XXX), // if using FeedbackDevice.AnalogEncoder or AnalogPot

        # set the peak and nominal outputs, 12V means full
        self.talon.configNominalOutputVoltage(+0.0, -0.0)
        self.talon.configPeakOutputVoltage(+12.0, 0.0)
        # set closed loop gains in slot0
        self.talon.setProfile(0)
        self.talon.setF(0.1097)
        self.talon.setP(0.22)
        self.talon.setI(0) 
        self.talon.setD(0)
    
    def teleopPeriodic(self):
        # get gamepad axis
        leftYstick = self.joy.getY()
        motorOutput = self.talon.getOutputVoltage() / self.talon.getBusVoltage()
        
        # prepare line to print
        msg = 'out: %8.2f spd: %8.2f' % (motorOutput, self.talon.getSpeed())
        
        if self.joy.getRawButton(1):
            # Speed mode
            targetSpeed = leftYstick * 1500.0 # 1500 RPM in either direction
            self.talon.changeControlMode(wpilib.CANTalon.ControlMode.Speed)
            self.talon.set(targetSpeed) # 1500 RPM in either direction

            # append more signals to print when in speed mode.
            msg += 'err: %4d trg: %8.2f' % (self.talon.getClosedLoopError(), targetSpeed)
        else:
            # Percent voltage mode
            self.talon.changeControlMode(wpilib.CANTalon.ControlMode.PercentVbus)
            self.talon.set(leftYstick)

        self.loops += 1
        if self.loops >= 10:
            self.loops = 0
            print(msg)

if __name__ == '__main__':
    wpilib.run(MyRobot)