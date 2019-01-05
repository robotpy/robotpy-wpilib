# validated: 2019-01-04 TW cbaff528500c edu/wpi/first/wpilibj/RobotDrive.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import List, Tuple

import hal
import math
import warnings
import weakref

from .motorsafety import MotorSafety
from .talon import Talon

__all__ = ["RobotDrive"]


def _freeRobotDrive(allocatedSpeedControllers) -> None:
    """
    Free the speed controllers if they were allocated locally
    """
    for sc in allocatedSpeedControllers:
        sc_close = getattr(sc, "close", None)
        if sc_close is not None:
            sc_close()
        elif hasattr(sc, "free"):
            sc.free()


class RobotDrive(MotorSafety):
    """
    .. deprecated:: 2018.0.0
        Use :class:`.DifferentialDrive` or :class:`.MecanumDrive` instead.

    Operations on a robot drivetrain based on a definition of the motor
    configuration.

    The robot drive class handles basic driving for a robot. Currently, 2
    and 4 motor tank and mecanum drive trains are supported. In the future
    other drive types like swerve might be implemented. Motor channel numbers
    are passed supplied on creation of the class. Those are used for either
    the drive function (intended for hand created drive code, such as
    autonomous) or with the Tank/Arcade functions intended to be used for
    Operator Control driving.
    
    .. not_implemented: setupMotorSafety
    """

    class MotorType:
        """The location of a motor on the robot for the purpose of driving."""

        #: Front left
        kFrontLeft = 0

        #: Front right
        kFrontRight = 1

        #: Rear left
        kRearLeft = 2

        #: Rear right
        kRearRight = 3

    kDefaultExpirationTime = 0.1
    kDefaultSensitivity = 0.5
    kDefaultMaxOutput = 1.0

    kMaxNumberOfMotors = 4

    kArcadeRatioCurve_Reported = False
    kTank_Reported = False
    kArcadeStandard_Reported = False
    kMecanumCartesian_Reported = False
    kMecanumPolar_Reported = False

    def __init__(self, *args, **kwargs) -> None:
        """Constructor for RobotDrive.

        Either 2 or 4 motors can be passed to the constructor to implement
        a two or four wheel drive system, respectively.

        When positional arguments are used, these are the two accepted orders:
        
        - leftMotor, rightMotor
        - frontLeftMotor, rearLeftMotor, frontRightMotor, rearRightMotor

        Alternatively, the above names can be used as keyword arguments.

        Either channel numbers or motor controllers can be passed (determined
        by whether the passed object has a `set` function).  If channel
        numbers are passed, the motorController keyword argument, if present,
        is the motor controller class to use; if unspecified, :class:`.Talon` is used.
        """
        warnings.warn(
            "RobotDrive was deprecated in 2018.0.0. Use DifferentialDrive, KilloughDrive, or MecanumDrive instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__()

        # keyword arguments
        self.frontLeftMotor = kwargs.pop("frontLeftMotor", None)
        self.rearLeftMotor = kwargs.pop("rearLeftMotor", None)
        self.frontRightMotor = kwargs.pop("frontRightMotor", None)
        self.rearRightMotor = kwargs.pop("rearRightMotor", None)

        if "leftMotor" in kwargs:
            self.rearLeftMotor = kwargs.pop("leftMotor")
        if "rightMotor" in kwargs:
            self.rearRightMotor = kwargs.pop("rightMotor")

        controllerClass = kwargs.pop("motorController", None)
        if controllerClass is None:
            controllerClass = Talon

        if kwargs:
            warnings.warn(
                "unknown keyword arguments: %s" % kwargs.keys(), RuntimeWarning
            )

        # positional arguments
        if len(args) == 2:
            self.rearLeftMotor = args[0]
            self.rearRightMotor = args[1]
        elif len(args) == 4:
            self.frontLeftMotor = args[0]
            self.rearLeftMotor = args[1]
            self.frontRightMotor = args[2]
            self.rearRightMotor = args[3]
        elif len(args) != 0:
            raise ValueError(
                "don't know how to handle %d positional arguments" % len(args)
            )

        self.allocatedSpeedControllers = list()

        # convert channel number into motor controller if needed
        if self.frontLeftMotor is not None and not hasattr(self.frontLeftMotor, "set"):
            self.frontLeftMotor = controllerClass(self.frontLeftMotor)
            self.allocatedSpeedControllers.append(self.frontLeftMotor)
        if self.rearLeftMotor is not None and not hasattr(self.rearLeftMotor, "set"):
            self.rearLeftMotor = controllerClass(self.rearLeftMotor)
            self.allocatedSpeedControllers.append(self.rearLeftMotor)
        if self.frontRightMotor is not None and not hasattr(
            self.frontRightMotor, "set"
        ):
            self.frontRightMotor = controllerClass(self.frontRightMotor)
            self.allocatedSpeedControllers.append(self.frontRightMotor)
        if self.rearRightMotor is not None and not hasattr(self.rearRightMotor, "set"):
            self.rearRightMotor = controllerClass(self.rearRightMotor)
            self.allocatedSpeedControllers.append(self.rearRightMotor)

        # other defaults
        self.maxOutput = RobotDrive.kDefaultMaxOutput
        self.sensitivity = RobotDrive.kDefaultSensitivity

        # set up motor safety
        self.setExpiration(self.kDefaultExpirationTime)
        self.setSafetyEnabled(True)

        # Setup Finalizer
        self.__finalizer = weakref.finalize(
            self, _freeRobotDrive, self.allocatedSpeedControllers
        )

        # start off not moving
        self.drive(0, 0)

    def drive(self, outputMagnitude: float, curve: float) -> None:
        """Drive the motors at "outputMagnitude" and "curve".

        Both outputMagnitude and curve are -1.0 to +1.0 values, where 0.0
        represents stopped and not turning. ``curve < 0`` will turn left and ``curve > 0``
        will turn right.

        The algorithm for steering provides a constant turn radius for any normal
        speed range, both forward and backward. Increasing m_sensitivity causes
        sharper turns for fixed values of curve.

        This function will most likely be used in an autonomous routine.

        :param outputMagnitude: The speed setting for the outside wheel in a turn,
               forward or backwards, +1 to -1.
        :param curve: The rate of turn, constant for different forward speeds. Set
               ``curve < 0`` for left turn or ``curve > 0`` for right turn.

        Set ``curve = e^(-r/w)`` to get a turn radius r for wheelbase w of your robot.
        Conversely, turn radius r = -ln(curve)*w for a given value of curve and
        wheelbase w.
        """
        if not RobotDrive.kArcadeRatioCurve_Reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                self.getNumMotors(),
                hal.UsageReporting.kRobotDrive_ArcadeRatioCurve,
            )
            RobotDrive.kArcadeRatioCurve_Reported = True

        if curve < 0:
            value = math.log(-curve)
            ratio = (value - self.sensitivity) / (value + self.sensitivity)
            if ratio == 0:
                ratio = 0.0000000001
            leftOutput = outputMagnitude / ratio
            rightOutput = outputMagnitude
        elif curve > 0:
            value = math.log(curve)
            ratio = (value - self.sensitivity) / (value + self.sensitivity)
            if ratio == 0:
                ratio = 0.0000000001
            leftOutput = outputMagnitude
            rightOutput = outputMagnitude / ratio
        else:
            leftOutput = outputMagnitude
            rightOutput = outputMagnitude

        self.setLeftRightMotorOutputs(leftOutput, rightOutput)

    def tankDrive(self, *args, **kwargs) -> None:
        """Provide tank steering using the stored robot configuration.

        Either two joysticks (with optional specified axis) or two raw values
        may be passed positionally, along with an optional squaredInputs
        boolean.  The valid positional combinations are:

        - leftStick, rightStick
        - leftStick, rightStick, squaredInputs
        - leftStick, leftAxis, rightStick, rightAxis
        - leftStick, leftAxis, rightStick, rightAxis, squaredInputs
        - leftValue, rightValue
        - leftValue, rightValue, squaredInputs

        Alternatively, the above names can be used as keyword arguments.
        The behavior of mixes of keyword arguments in other than the
        combinations above is undefined.

        If specified positionally, the value and joystick versions are
        disambiguated by looking for a `getY` function.

        :param leftStick: The joystick to control the left side of the robot.
        :param leftAxis: The axis to select on the left side Joystick object
            (defaults to the Y axis if unspecified).
        :param rightStick: The joystick to control the right side of the robot.
        :param rightAxis: The axis to select on the right side Joystick object
            (defaults to the Y axis if unspecified).
        :param leftValue: The value to control the left side of the robot.
        :param rightValue: The value to control the right side of the robot.
        :param squaredInputs: Setting this parameter to True decreases the
            sensitivity at lower speeds.  Defaults to True if unspecified.
        """
        if not RobotDrive.kTank_Reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                self.getNumMotors(),
                hal.UsageReporting.kRobotDrive_Tank,
            )
            RobotDrive.kTank_Reported = True

        # keyword arguments
        leftStick = kwargs.pop("leftStick", None)
        rightStick = kwargs.pop("rightStick", None)
        leftAxis = kwargs.pop("leftAxis", None)
        rightAxis = kwargs.pop("rightAxis", None)
        leftValue = kwargs.pop("leftValue", None)
        rightValue = kwargs.pop("rightValue", None)
        squaredInputs = kwargs.pop("squaredInputs", None)

        if kwargs:
            warnings.warn(
                "unknown keyword arguments: %s" % kwargs.keys(), RuntimeWarning
            )

        # positional arguments
        if len(args) == 2 or len(args) == 3:
            left, right = args[0:2]
            if len(args) == 3:
                squaredInputs = args[2]
            # determine if stick or value
            if hasattr(left, "getY"):
                leftStick = left
            else:
                leftValue = left
            if hasattr(right, "getY"):
                rightStick = right
            else:
                rightValue = right
        elif len(args) == 4:
            leftStick, leftAxis, rightStick, rightAxis = args
        elif len(args) == 5:
            leftStick, leftAxis, rightStick, rightAxis, squaredInputs = args
        elif len(args) != 0:
            raise ValueError(
                "don't know how to handle %d positional arguments" % len(args)
            )

        # get value from stick if only stick provided
        if leftValue is None:
            if leftAxis is None:
                leftValue = leftStick.getY()
            else:
                leftValue = leftStick.getRawAxis(leftAxis)
        if rightValue is None:
            if rightAxis is None:
                rightValue = rightStick.getY()
            else:
                rightValue = rightStick.getRawAxis(rightAxis)

        # default to squared inputs if unspecified
        if squaredInputs is None:
            squaredInputs = True

        # square the inputs (while preserving the sign) to increase fine
        # control while permitting full power
        leftValue = RobotDrive.limit(leftValue)
        rightValue = RobotDrive.limit(rightValue)
        if squaredInputs:
            leftValue = math.copysign(leftValue * leftValue, leftValue)
            rightValue = math.copysign(rightValue * rightValue, rightValue)

        self.setLeftRightMotorOutputs(leftValue, rightValue)

    def arcadeDrive(self, *args, **kwargs) -> None:
        """Provide tank steering using the stored robot configuration.

        Either one or two joysticks (with optional specified axis) or two raw
        values may be passed positionally, along with an optional
        squaredInputs boolean.  The valid positional combinations are:

        - stick
        - stick, squaredInputs
        - moveStick, moveAxis, rotateStick, rotateAxis
        - moveStick, moveAxis, rotateStick, rotateAxis, squaredInputs
        - moveValue, rotateValue
        - moveValue, rotateValue, squaredInputs

        Alternatively, the above names can be used as keyword arguments.
        The behavior of mixes of keyword arguments in other than the
        combinations above is undefined.

        If specified positionally, the value and joystick versions are
        disambiguated by looking for a `getY` function on the stick.

        :param stick: The joystick to use for Arcade single-stick driving.
            The Y-axis will be selected for forwards/backwards and the
            X-axis will be selected for rotation rate.
        :param moveStick: The Joystick object that represents the
            forward/backward direction.
        :param moveAxis: The axis on the moveStick object to use for
            forwards/backwards (typically Y_AXIS).
        :param rotateStick: The Joystick object that represents the rotation
            value.
        :param rotateAxis: The axis on the rotation object to use for the
            rotate right/left (typically X_AXIS).
        :param moveValue: The value to use for forwards/backwards.
        :param rotateValue: The value to use for the rotate right/left.
        :param squaredInputs: Setting this parameter to True decreases the
            sensitivity at lower speeds.  Defaults to True if unspecified.
        """

        if not RobotDrive.kArcadeStandard_Reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                self.getNumMotors(),
                hal.UsageReporting.kRobotDrive_ArcadeStandard,
            )
            RobotDrive.kArcadeStandard_Reported = True

        # keyword arguments
        stick = kwargs.pop("stick", None)
        moveStick = kwargs.pop("moveStick", None)
        rotateStick = kwargs.pop("rotateStick", None)
        moveAxis = kwargs.pop("moveAxis", None)
        rotateAxis = kwargs.pop("rotateAxis", None)
        moveValue = kwargs.pop("moveValue", None)
        rotateValue = kwargs.pop("rotateValue", None)
        squaredInputs = kwargs.pop("squaredInputs", None)

        if kwargs:
            warnings.warn(
                "unknown keyword arguments: %s" % kwargs.keys(), RuntimeWarning
            )

        # positional arguments
        if len(args) == 1:
            stick = args[0]
        elif len(args) == 2:
            # determine if stick or value
            if hasattr(args[0], "getY"):
                stick, squaredInputs = args
            else:
                moveValue, rotateValue = args
        elif len(args) == 3:
            moveValue, rotateValue, squaredInputs = args
        elif len(args) == 4:
            moveStick, moveAxis, rotateStick, rotateAxis = args
        elif len(args) == 5:
            moveStick, moveAxis, rotateStick, rotateAxis, squaredInputs = args
        elif len(args) != 0:
            raise ValueError(
                "don't know how to handle %d positional arguments" % len(args)
            )

        # get value from stick if only stick provided
        if moveValue is None:
            if moveStick is None:
                moveValue = stick.getY()
            else:
                moveValue = moveStick.getRawAxis(moveAxis)
        if rotateValue is None:
            if rotateStick is None:
                rotateValue = stick.getX()
            else:
                rotateValue = rotateStick.getRawAxis(rotateAxis)

        # default to squared inputs if unspecified
        if squaredInputs is None:
            squaredInputs = True

        # local variables to hold the computed PWM values for the motors
        moveValue = RobotDrive.limit(moveValue)
        rotateValue = RobotDrive.limit(rotateValue)

        if squaredInputs:
            # square the inputs (while preserving the sign) to increase fine
            # control while permitting full power
            moveValue = math.copysign(moveValue * moveValue, moveValue)
            rotateValue = math.copysign(rotateValue * rotateValue, rotateValue)

        if moveValue > 0.0:
            if rotateValue > 0.0:
                leftMotorSpeed = moveValue - rotateValue
                rightMotorSpeed = max(moveValue, rotateValue)
            else:
                leftMotorSpeed = max(moveValue, -rotateValue)
                rightMotorSpeed = moveValue + rotateValue
        else:
            if rotateValue > 0.0:
                leftMotorSpeed = -max(-moveValue, rotateValue)
                rightMotorSpeed = moveValue + rotateValue
            else:
                leftMotorSpeed = moveValue - rotateValue
                rightMotorSpeed = -max(-moveValue, -rotateValue)

        self.setLeftRightMotorOutputs(leftMotorSpeed, rightMotorSpeed)

    def mecanumDrive_Cartesian(
        self, x: float, y: float, rotation: float, gyroAngle: float
    ) -> None:
        """Drive method for Mecanum wheeled robots.

        A method for driving with Mecanum wheeled robots. There are 4 wheels
        on the robot, arranged so that the front and back wheels are toed in
        45 degrees.  When looking at the wheels from the top, the roller
        axles should form an X across the robot.

        This is designed to be directly driven by joystick axes.

        :param x: The speed that the robot should drive in the X direction.
            [-1.0..1.0]
        :param y: The speed that the robot should drive in the Y direction.
            This input is inverted to match the forward == -1.0 that
            joysticks produce. [-1.0..1.0]
        :param rotation: The rate of rotation for the robot that is
            completely independent of the translation. [-1.0..1.0]
        :param gyroAngle: The current angle reading from the gyro.  Use this
            to implement field-oriented controls.
        """
        if not RobotDrive.kMecanumCartesian_Reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                self.getNumMotors(),
                hal.UsageReporting.kRobotDrive_MecanumCartesian,
            )
            RobotDrive.kMecanumCartesian_Reported = True

        xIn = x
        yIn = y
        # Negate y for the joystick.
        yIn = -yIn
        # Compensate for gyro angle.
        xIn, yIn = RobotDrive.rotateVector(xIn, yIn, gyroAngle)

        wheelSpeeds = [0] * self.kMaxNumberOfMotors
        wheelSpeeds[self.MotorType.kFrontLeft] = xIn + yIn + rotation
        wheelSpeeds[self.MotorType.kFrontRight] = -xIn + yIn - rotation
        wheelSpeeds[self.MotorType.kRearLeft] = -xIn + yIn + rotation
        wheelSpeeds[self.MotorType.kRearRight] = xIn + yIn - rotation

        RobotDrive.normalize(wheelSpeeds)

        self.frontLeftMotor.set(wheelSpeeds[self.MotorType.kFrontLeft] * self.maxOutput)
        self.frontRightMotor.set(
            wheelSpeeds[self.MotorType.kFrontRight] * self.maxOutput
        )
        self.rearLeftMotor.set(wheelSpeeds[self.MotorType.kRearLeft] * self.maxOutput)
        self.rearRightMotor.set(wheelSpeeds[self.MotorType.kRearRight] * self.maxOutput)

        self.feed()

    def mecanumDrive_Polar(
        self, magnitude: float, direction: float, rotation: float
    ) -> None:
        """Drive method for Mecanum wheeled robots.

        A method for driving with Mecanum wheeled robots. There are 4 wheels
        on the robot, arranged so that the front and back wheels are toed in
        45 degrees.  When looking at the wheels from the top, the roller
        axles should form an X across the robot.

        :param magnitude: The speed that the robot should drive in a given
            direction.
        :param direction: The direction the robot should drive in degrees.
            The direction and maginitute are independent of the rotation rate.
        :param rotation: The rate of rotation for the robot that is completely
            independent of the magnitute or direction. [-1.0..1.0]
        """
        if not RobotDrive.kMecanumPolar_Reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                self.getNumMotors(),
                hal.UsageReporting.kRobotDrive_MecanumPolar,
            )
            RobotDrive.kMecanumPolar_Reported = True

        # Normalized for full power along the Cartesian axes.
        magnitude = RobotDrive.limit(magnitude) * math.sqrt(2.0)
        # The rollers are at 45 degree angles.
        dirInRad = math.radians(direction + 45.0)
        cosD = math.cos(dirInRad)
        sinD = math.sin(dirInRad)

        wheelSpeeds = [0] * self.kMaxNumberOfMotors
        wheelSpeeds[self.MotorType.kFrontLeft] = sinD * magnitude + rotation
        wheelSpeeds[self.MotorType.kFrontRight] = cosD * magnitude - rotation
        wheelSpeeds[self.MotorType.kRearLeft] = cosD * magnitude + rotation
        wheelSpeeds[self.MotorType.kRearRight] = sinD * magnitude - rotation

        RobotDrive.normalize(wheelSpeeds)

        self.frontLeftMotor.set(wheelSpeeds[self.MotorType.kFrontLeft] * self.maxOutput)
        self.frontRightMotor.set(
            wheelSpeeds[self.MotorType.kFrontRight] * self.maxOutput
        )
        self.rearLeftMotor.set(wheelSpeeds[self.MotorType.kRearLeft] * self.maxOutput)
        self.rearRightMotor.set(wheelSpeeds[self.MotorType.kRearRight] * self.maxOutput)

        self.feed()

    def holonomicDrive(
        self, magnitude: float, direction: float, rotation: float
    ) -> None:
        """Holonomic Drive method for Mecanum wheeled robots.

        This is an alias to :func:`mecanumDrive_Polar` for backward
        compatibility.

        :param magnitude: The speed that the robot should drive in a given
            direction.  [-1.0..1.0]
        :param direction: The direction the robot should drive. The direction
            and magnitude are independent of the rotation rate.
        :param rotation: The rate of rotation for the robot that is
            completely independent of the magnitude or direction.  [-1.0..1.0]
        """
        self.mecanumDrive_Polar(magnitude, direction, rotation)

    def setLeftRightMotorOutputs(self, leftOutput: float, rightOutput: float) -> None:
        """Set the speed of the right and left motors.

        This is used once an appropriate drive setup function is called such as
        twoWheelDrive(). The motors are set to "leftSpeed" and "rightSpeed"
        and includes flipping the direction of one side for opposing motors.

        :param leftOutput: The speed to send to the left side of the robot.
        :param rightOutput: The speed to send to the right side of the robot.
        """
        if self.rearLeftMotor is None or self.rearRightMotor is None:
            raise ValueError("Null motor provided")

        leftOutput = RobotDrive.limit(leftOutput) * self.maxOutput
        rightOutput = RobotDrive.limit(rightOutput) * self.maxOutput

        if self.frontLeftMotor is not None:
            self.frontLeftMotor.set(leftOutput)
        self.rearLeftMotor.set(leftOutput)

        if self.frontRightMotor is not None:
            self.frontRightMotor.set(-rightOutput)
        self.rearRightMotor.set(-rightOutput)

        self.feed()

    @staticmethod
    def limit(number: float) -> float:
        """Limit motor values to the -1.0 to +1.0 range."""
        if number > 1.0:
            return 1.0
        if number < -1.0:
            return -1.0
        return number

    @staticmethod
    def normalize(wheelSpeeds: List[float]) -> None:
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1.0.
        """
        maxMagnitude = max(abs(x) for x in wheelSpeeds)
        if maxMagnitude > 1.0:
            for i in range(len(wheelSpeeds)):
                wheelSpeeds[i] = wheelSpeeds[i] / maxMagnitude

    @staticmethod
    def rotateVector(x: float, y: float, angle: float) -> Tuple[float, float]:
        """Rotate a vector in Cartesian space."""
        angle = math.radians(angle)
        cosA = math.cos(angle)
        sinA = math.sin(angle)
        return (x * cosA - y * sinA), (x * sinA + y * cosA)

    def setInvertedMotor(self, motor: int, isInverted: bool) -> bool:
        """Invert a motor direction.

        This is used when a motor should run in the opposite direction as
        the drive code would normally run it. Motors that are direct drive
        would be inverted, the drive code assumes that the motors are geared
        with one reversal.

        :param motor: The motor index to invert.
        :param isInverted: True if the motor should be inverted when operated.
        """
        if motor == self.MotorType.kFrontLeft:
            self.frontLeftMotor.setInverted(isInverted)
        elif motor == self.MotorType.kFrontRight:
            self.frontRightMotor.setInverted(isInverted)
        elif motor == self.MotorType.kRearLeft:
            self.rearLeftMotor.setInverted(isInverted)
        elif motor == self.MotorType.kRearRight:
            self.rearRightMotor.setInverted(isInverted)
        else:
            raise ValueError("Invalid motor type specified")

    def setSensitivity(self, sensitivity: float) -> None:
        """Set the turning sensitivity.

        This only impacts the drive() entry-point.

        :param sensitivity: Effectively sets the turning sensitivity (or turn
            radius for a given value)
        """
        self.sensitivity = sensitivity

    def setMaxOutput(self, maxOutput: float) -> None:
        """Configure the scaling factor for using RobotDrive with motor
        controllers in a mode other than PercentVbus.

        :param maxOutput: Multiplied with the output percentage computed by
            the drive functions.
        """
        self.maxOutput = maxOutput

    def free(self) -> None:
        self.__finalizer()
        self.frontLeftMotor = None
        self.frontRightMotor = None
        self.rearLeftMotor = None
        self.rearRightMotor = None
        self.allocatedSpeedControllers = list()
        self.setSafetyEnabled(False)

    def getDescription(self) -> str:
        return "Robot Drive"

    def stopMotor(self) -> None:
        if self.frontLeftMotor is not None:
            self.frontLeftMotor.stopMotor()
        if self.frontRightMotor is not None:
            self.frontRightMotor.stopMotor()
        if self.rearLeftMotor is not None:
            self.rearLeftMotor.stopMotor()
        if self.rearRightMotor is not None:
            self.rearRightMotor.stopMotor()
        self.feed()

    def getNumMotors(self) -> int:
        motors = 0
        if self.frontLeftMotor is not None:
            motors += 1
        if self.frontRightMotor is not None:
            motors += 1
        if self.rearLeftMotor is not None:
            motors += 1
        if self.rearRightMotor is not None:
            motors += 1
        return motors
