
import wpilib
from wpilib.command import PIDSubsystem

class Elevator(PIDSubsystem):
    '''
    The elevator subsystem uses PID to go to a given height. Unfortunately,
    in it's current state PID values for simulation are different than in
    the real world due to minor differences.
    '''
    
    kP_real = 4
    kI_real = 0.07
    kP_simulation = 18
    kI_simulation = 0.2
    
    def __init__(self, robot):
        super().__init__(self.kP_real, self.kI_real, 0)
        
        # Check for simulation and update PID values
        if robot.isSimulation():
            self.getPIDController().setPID(self.kP_simulation, self.kI_simulation, 0, 0)
            
        self.setAbsoluteTolerance(0.005)
        
        self.motor = wpilib.Victor(5)
        
        # Conversion value of potentiometer varies between the real world and simulation
        if robot.isReal():
            self.pot = wpilib.AnalogPotentiometer(2, -2.0/5)
        else:
            self.pot = wpilib.AnalogPotentiometer(2)    # defaults to meters
            
        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator("Elevator", "Motor", self.motor)
        wpilib.LiveWindow.addSensor("Elevator", "Pot", self.pot)
        wpilib.LiveWindow.addActuator("Elevator", "PID", self.getPIDController())
        
    def log(self):
        '''The log method puts interesting information to the SmartDashboard.'''
        wpilib.SmartDashboard.putData("Elevator Pot", self.pot)
        
    def returnPIDInput(self):
        '''Use the potentiometer as the PID sensor. This method is automatically
           called by the subsystem'''
        return self.pot.get()
    
    def usePIDOutput(self, output):
        '''Use the motor as the PID output. This method is automatically called by
           the subsystem'''
        self.motor.set(output)
