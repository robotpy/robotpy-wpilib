
import wpilib
from wpilib.command import PIDSubsystem

class Wrist(PIDSubsystem):
    '''
    The wrist subsystem is like the elevator, but with a rotational joint instead
    of a linear joint. 
    '''
    
    kP_real = 1
    kP_simulation = 0.05
    
    def __init__(self, robot):
        super().__init__(self.kP_real, 0, 0)
        
        # Check for simulation and update PID values
        if robot.isSimulation():
            self.getPIDController().setPID(self.kP_simulation, 0, 0, 0)
            
        self.setAbsoluteTolerance(2.5)
        
        self.motor = wpilib.Victor(6)
        
        # Conversion value of potentiometer varies between the real world and simulation
        if robot.isReal():
            self.pot = wpilib.AnalogPotentiometer(3, -270/5)
        else:
            self.pot = wpilib.AnalogPotentiometer(3)    # defaults to degrees
            
        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator("Wrist", "Motor", self.motor)
        wpilib.LiveWindow.addSensor("Wrist", "Pot", self.pot)
        wpilib.LiveWindow.addActuator("Wrist", "PID", self.getPIDController())
        
    def log(self):
        '''The log method puts interesting information to the SmartDashboard.'''
        wpilib.SmartDashboard.putData("Wrist Angle", self.pot)
        
    def returnPIDInput(self):
        '''Use the potentiometer as the PID sensor. This method is automatically
           called by the subsystem'''
        return self.pot.get()
    
    def usePIDOutput(self, output):
        '''Use the motor as the PID output. This method is automatically called by
           the subsystem'''
        self.motor.set(output)
