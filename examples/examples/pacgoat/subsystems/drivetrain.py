import wpilib
import math
from wpilib.command import Subsystem
from global_vars import subsystems, is_real
from commands.drive_with_joystick import DriveWithJoystick


class DriveTrain(Subsystem):
    """
    The DriveTrain subsystem controls the robot's chassis and reads in
    information about it's speed and position.
    """

    def __init__(self):
        #Configure drive motors
        self.front_left_cim = wpilib.Victor(1)
        self.front_right_cim = wpilib.Victor(2)
        self.back_left_cim = wpilib.Victor(3)
        self.back_right_cim = wpilib.Victor(4)
        wpilib.LiveWindow.addActuator("DriveTrain", "Front Left CIM", self.front_left_cim)
        wpilib.LiveWindow.addActuator("DriveTrain", "Front Right CIM", self.front_right_cim)
        wpilib.LiveWindow.addActuator("DriveTrain", "Back Left CIM", self.back_left_cim)
        wpilib.LiveWindow.addActuator("DriveTrain", "Back Right CIM", self.back_right_cim)

        #Configure the RobotDrive to reflect the fact that all our motors are
        #wired backwards and our drivers sensitivity preferences.
        self.drive = wpilib.RobotDrive(self.front_left_cim, self.front_right_cim, self.back_left_cim, self.back_right_cim)
        self.drive.setSafetyEnabled(True)
        self.drive.setExpiration(.1)
        self.drive.setSensitivity(.5)
        self.drive.setMaxOutput(1.0)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kFrontLeft, True)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kFrontRight, True)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearLeft, True)
        self.drive.setInvertedMotor(wpilib.RobotDrive.MotorType.kRearRight, True)

        #Configure encoders
        self.right_encoder = wpilib.Encoder(1, 2, True, wpilib.Encoder.EncodingType.k4X)
        self.left_encoder = wpilib.Encoder(3, 4, False, wpilib.Encoder.EncodingType.k4X)
        self.right_encoder.setPIDSourceParameter(wpilib.Encoder.PIDSourceParameter.kDistance)
        self.left_encoder.setPIDSourceParameter(wpilib.Encoder.PIDSourceParameter.kDistance)

        if is_real():
            #Converts to feet
            self.right_encoder.setDistancePerPulse(0.0785398)
            self.left_encoder.setDistancePerPulse(0.0785398)
        else:
            #Convert to feet 4in diameter wheels with 360 tick simulated encoders.
            self.right_encoder.setDistancePerPulse((4*math.pi)/(360*12))
            self.left_encoder.setDistancePerPulse((4*math.pi)/(360*12))

        wpilib.LiveWindow.addSensor("DriveTrain", "Right Encoder", self.right_encoder)
        wpilib.LiveWindow.addSensor("DriveTrain", "Left Encoder", self.left_encoder)

        #Configure gyro
        self.gyro = wpilib.Gyro(2)
        if is_real():
            #TODO: Handle more gracefully
            self.gyro.setSensitivity(0.007)

        wpilib.LiveWindow.addSensor("DriveTrain", "Gyro", self.gyro)

    def initDefaultCommand(self):
        """
        When other commands aren't using the drivetrain, allow tank drive with the joystick.
        """
        self.setDefaultCommand(DriveWithJoystick())

    def tank_drive(self, *args, **kwargs):
        joy = kwargs.pop("joy", None)

        if len(args) == 1:
            joy = args[0]

        if joy is not None:
            self.drive.tankDrive(joy.getY(), joy.getRawAxis(4))
        else:
            self.drive.tankDrive(*args, **kwargs)

    def stop(self):
        """Stop the drivetrain from moving."""
        self.tank_drive(0, 0)

    def get_left_encoder(self):
        """:return The encoder getting the distance and speed of the right side of the drivetrain."""
        return self.left_encoder

    def get_right_encoder(self):
        """:return The encoder getting the distance and speed of the right side of the drivetrain."""
        return self.right_encoder

    def get_angle(self):
        """:return The current angle of the drivetrain."""
        return self.gyro.getAngle()