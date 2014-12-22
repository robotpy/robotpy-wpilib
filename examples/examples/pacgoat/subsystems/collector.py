
import wpilib
from wpilib.command import Subsystem


class Collector(Subsystem):
    """
    The Collector subsystem has one motor for the rollers, a limit switch for ball
    detection, a piston for opening and closing the claw, and a reed switch to
    detect if the piston is open.
    """

    FORWARD = 1
    STOP = 0
    REVERSE = -1

    def __init__(self, robot):
        # Configure devices
        self.rollerMotor = wpilib.Victor(6)
        self.ballDetector = wpilib.DigitalInput(10)
        self.openDetector = wpilib.DigitalInput(6)
        self.piston = wpilib.Solenoid(0, 1)
        self.robot = robot

        # Put everything to the LiveWindow for testing.
        wpilib.LiveWindow.addActuator("Collector", "Roller Motor", self.rollerMotor)
        wpilib.LiveWindow.addSensor("Collector", "Ball Detector", self.ballDetector)
        wpilib.LiveWindow.addSensor("Collector", "Claw Open Detector", self.openDetector)
        wpilib.LiveWindow.addActuator("Collector", "Piston", self.piston)

        super().__init__()

    def hasBall(self):
        """
        NOTE: The current simulation model uses the the lower part of the claw
        since the limit switch wasn't exported. At some point, this will be
        updated.

        :returns: Whether or not the robot has the ball.
        """
        return self.ballDetector.get() # TODO: prepend ! to reflect real robot

    def setSpeed(self, speed):
        """:param speed: The speed to spin the rollers."""
        self.rollerMotor.set(-speed)

    def stop(self):
        """Stop the rollers from spinning"""
        self.rollerMotor.set(0)

    def isOpen(self):
        """:returns: Whether or not the claw is open"""
        return self.openDetector.get() # TODO: prepend ! to reflect real robot

    def open(self):
        """Open the claw up. (For shooting)"""
        self.piston.set(True)

    def close(self):
        """Close the claw. (For collecting and driving)"""
        self.piston.set(False)

    def initDefaultCommand(self):
        """No Default Command"""
        pass