
import wpilib
from wpilib.command import PIDSubsystem


class Pivot(PIDSubsystem):
    """
    The Pivot subsystem contains the Van-door motor and tha pot for PID control
    of angle of the pivot and claw.
    """

    # Constants for some useful angles
    COLLECT = 105
    LOW_GOAL = 90
    SHOOT = 45
    SHOOT_NEAR = 30

    def __init__(self, robot):
        super().__init__(7.0, 0.0, 8.0, name="Pivot")
        self.robot = robot
        self.setAbsoluteTolerance(0.005)
        self.getPIDController().setContinuous(False)
        if robot.isSimulation():
            # PID is different in simulation.
            self.getPIDController().setPID(0.5, 0.001, 2)
            self.setAbsoluteTolerance(5)

        # Motor to move the pivot
        self.motor = wpilib.Victor(5)

        # Sensors for measuring the position of the pivot.
        self.upperLimitSwitch = wpilib.DigitalInput(13)
        self.lowerLimitSwitch = wpilib.DigitalInput(12)

        # 0 degrees is vertical facing up.
        # Angle increases the more forward the pivot goes.
        self.pot = wpilib.AnalogPotentiometer(1)

        # Put everything to the LiveWindow for testing.
        wpilib.LiveWindow.addSensor("Pivot", "Upper Limit Switch", self.upperLimitSwitch)
        wpilib.LiveWindow.addSensor("Pivot", "Lower Limit Switch", self.lowerLimitSwitch)
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

    def isAtUpperLimit(self):
        """:return If the pivot is at its upper limit."""
        return self.upperLimitSwitch.get()

    def isAtLowerLimit(self):
        """:return If the pivot is at its lower limit."""
        return self.lowerLimitSwitch.get()

    def getAngle(self):
        """:return the current angle of the pivot."""
        return self.pot.get()
