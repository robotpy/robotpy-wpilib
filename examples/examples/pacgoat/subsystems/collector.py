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
        #Configure devices
        self.roller_motor = wpilib.Victor(5)
        self.ball_detector = wpilib.DigitalInput(9)
        self.open_detector = wpilib.DigitalInput(5)
        self.piston = wpilib.Solenoid(0, 0)
        self.robot = robot

        #Put everything to the LiveWindow for testing.
        wpilib.LiveWindow.addActuator("Collector", "Roller Motor", self.roller_motor)
        wpilib.LiveWindow.addSensor("Collector", "Ball Detector", self.ball_detector)
        wpilib.LiveWindow.addSensor("Collector", "Claw Open Detector", self.open_detector)
        wpilib.LiveWindow.addActuator("Collector", "Piston", self.piston)

        super().__init__()

    def has_ball(self):
        """
        NOTE: The current simulation model uses the the lower part of the claw
        since the limit switch wasn't exported. At some point, this will be
        updated.

        :return Whether or not the robot has the ball.
        """
        return self.ball_detector.get()

    def set_speed(self, speed):
        """:param speed: The speed to spin the rollers."""
        self.roller_motor.set(-speed)

    def stop(self):
        """Stop the rollers from spinning"""
        self.roller_motor.set(0)

    def is_open(self):
        """:return Whether or not the claw is open"""
        return self.open_detector.get()

    def open(self):
        self.piston.set(True)

    def close(self):
        self.piston.set(False)

    def initDefaultCommand(self):
        """No Default Command"""
        pass