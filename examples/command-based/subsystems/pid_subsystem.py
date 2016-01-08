
from wpilib.command import PIDSubsystem


#This is a template PID Subsystem, PIDSubsystemName should, of course, be replaced by the
#name of your desired PIDSubsystem
class PIDSubsystemName(PIDSubsystem):

    def __init__(self, robot, p, i, d, period=None, f=0.0, name=None):
        # Use these to get going:
        # setSetpoint() -  Sets where the PID controller should move the system
        #                  to
        # enable() - Enables the PID controller.
        super().__init__(p, i, d, period, f, name)
        self.robot = robot

    def initDefaultCommand(self):
        #Set the default command for a subsystem here.
        pass

    def returnPIDInput(self):
        # Return your input value for the PID loop
        # e.g. a sensor, like a potentiometer:
        # your_pot.getAverageVoltage() / k_your_max_voltage;
        return 0

    def usePIDOutput(self, output):
        #Use output to drive your system, like a motor
        #e.g. your_motor.set(output)
        pass
