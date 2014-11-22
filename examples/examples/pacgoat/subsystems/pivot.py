import wpilib
from wpilib.command import PIDSubsystem


class Pivot(PIDSubsystem):
    """
    The Pivot subsystem contains the Van-door motor and tha pot for PID control
    of angle of the pivot and claw.
    """

    #Constants for some useful angles
    COLLLECT = 105
    LOW_GOAL = 90
    SHOOT = 45
    SHOOT_NEAR = 30

    def __init__(self, robot):
        super().__init__(7, 0, 8, name="Pivot")
        self.robot = robot
        self.setAbsoluteTolerance(0.005)
        self.getPIDController().setContinuous(False)
        if robot.is_simulated():
            #PID is different in simulation.
            self.getPIDController().setPID(0.5, 0.001, 2)
            self.setAbsoluteTolerance(5)

        #Motor to move the pivot
        self.motor = wpilib.Victor(4)

        #Sensors for measuring the position of the pivot.
        self.upper_limit_switch = wpilib.DigitalInput(12)
        self.lower_limit_switch = wpilib.DigitalInput(11)

        #0 degrees is vertical facing up.
        #Angle increases the more forward the pivot goes.
        self.pot = wpilib.AnalogPotentiometer(0)

        #Put everything to the LiveWindow for testing.
        wpilib.LiveWindow.addSensor("Pivot", "Upper Limit Switch", self.upper_limit_switch)
        wpilib.LiveWindow.addSensor("Pivot", "Lower Limit Switch", self.lower_limit_switch)
        wpilib.LiveWindow.addSensor("Pivot", "Pot", self.pot)
        wpilib.LiveWindow.addActuator("Pivot", "Motor", self.motor)
        wpilib.LiveWindow.addActuator("Pivot", "PIDSubsystem Controller", self.getPIDController())

    def initDefaultCommand(self):
        """No default command, if PID is enabled, the current setpoint will be maintained."""
        pass

    def returnPIDInput(self):
        """:return the angle read in by the potentiometer."""
        return self.pot.get()

    def usePIDOutput(self, output):
        """Set the motor speed based off the PID output."""
        self.motor.pidWrite(output)

    def is_at_upper_limit(self):
        """:return If the pivot is at its upper limit."""
        return self.upper_limit_switch.get()

    def is_at_lower_limit(self):
        """:return If the pivot is at its lower limit."""
        return self.lower_limit_switch.get()

    def get_angle(self):
        """:return the current angle of the pivot."""
        return self.pot.get()
