
import math

import wpilib
from wpilib.command import Subsystem

from commands.drive_with_joystick import DriveWithJoystick


class DriveTrain(Subsystem):
    """
    The DriveTrain subsystem controls the robot's chassis and reads in
    information about it's speed and position.
    """

    def __init__(self, robot):

        self.robot = robot

        # Configure drive motors
        self.frontLeftCIM = wpilib.Victor(1)
        self.frontRightCIM = wpilib.Victor(2)
        self.backLeftCIM = wpilib.Victor(3)
        self.backRightCIM = wpilib.Victor(4)
        wpilib.LiveWindow.addActuator("DriveTrain", "Front Left CIM", self.frontLeftCIM)
        wpilib.LiveWindow.addActuator("DriveTrain", "Front Right CIM", self.frontRightCIM)
        wpilib.LiveWindow.addActuator("DriveTrain", "Back Left CIM", self.backLeftCIM)
        wpilib.LiveWindow.addActuator("DriveTrain", "Back Right CIM", self.backRightCIM)

        # Configure the RobotDrive to reflect the fact that all our motors are
        # wired backwards and our drivers sensitivity preferences.
        self.drive = wpilib.RobotDrive(self.frontLeftCIM, self.frontRightCIM, self.backLeftCIM, self.backRightCIM)
        self.drive.setSafetyEnabled(True)
        self.drive.setExpiration(.1)
        self.drive.setSensitivity(.5)
        self.drive.setMaxOutput(1.0)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kFrontLeft, True)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kFrontRight, True)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearLeft, True)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearRight, True)

        # Configure encoders
        self.rightEncoder = wpilib.Encoder(1, 2,
                                           reverseDirection=True,
                                           encodingType=wpilib.Encoder.EncodingType.k4X)
        self.leftEncoder = wpilib.Encoder(3, 4,
                                          reverseDirection=False,
                                          encodingType=wpilib.Encoder.EncodingType.k4X)
        self.rightEncoder.setPIDSourceType(wpilib.Encoder.PIDSourceType.kDisplacement)
        self.leftEncoder.setPIDSourceType(wpilib.Encoder.PIDSourceType.kDisplacement)

        if robot.isReal():
            # Converts to feet
            self.rightEncoder.setDistancePerPulse(0.0785398)
            self.leftEncoder.setDistancePerPulse(0.0785398)
        else:
            # Convert to feet 4in diameter wheels with 360 tick simulated encoders.
            self.rightEncoder.setDistancePerPulse((4*math.pi)/(360*12))
            self.leftEncoder.setDistancePerPulse((4*math.pi)/(360*12))

        wpilib.LiveWindow.addSensor("DriveTrain", "Right Encoder", self.rightEncoder)
        wpilib.LiveWindow.addSensor("DriveTrain", "Left Encoder", self.leftEncoder)

        # Configure gyro
        # -> the original pacgoat example is at channel 2, but that was before WPILib
        #    moved to zero-based indexing. You need to change the gyro channel in
        #    /usr/share/frcsim/models/PacGoat/robots/PacGoat.SDF, from 2 to 0. 
        self.gyro = wpilib.AnalogGyro(0)
        if robot.isReal():
            # TODO: Handle more gracefully
            self.gyro.setSensitivity(0.007)

        wpilib.LiveWindow.addSensor("DriveTrain", "Gyro", self.gyro)

        super().__init__()

    def initDefaultCommand(self):
        """
        When other commands aren't using the drivetrain, allow tank drive with
        the joystick.
        """
        self.setDefaultCommand(DriveWithJoystick(self.robot))

    def tankDriveJoystick(self, joy):
        self.drive.tankDrive(joy.getY(), joy.getRawAxis(4))

    def tankDriveManual(self, leftAxis, rightAxis):
        self.drive.tankDrive(leftAxis, rightAxis)

    def stop(self):
        """Stop the drivetrain from moving."""
        self.tankDriveManual(0, 0)

    def getLeftEncoder(self):
        """:returns: The encoder getting the distance and speed of the right side of the drivetrain."""
        return self.leftEncoder

    def getRightEncoder(self):
        """:returns: The encoder getting the distance and speed of the right side of the drivetrain."""
        return self.rightEncoder

    def getAngle(self):
        """:returns: The current angle of the drivetrain."""
        return self.gyro.getAngle()
    