#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import math
import warnings

from .motorsafety import MotorSafety
from .talon import Talon

class RobotDrive(MotorSafety):
    """Utility class for handling Robot drive based on a definition of the
    motor configuration.  The robot drive class handles basic driving for a
    robot. Currently, 2 and 4 motor standard drive trains are supported. In
    the future other drive types like swerve and meccanum might be
    implemented. Motor channel numbers are passed supplied on creation of
    the class. Those are used for either the drive function (intended for
    hand created drive code, such as autonomous) or with the Tank/Arcade
    functions intended to be used for Operator Control driving.
    """

    class MotorType:
        """The location of a motor on the robot for the purpose of driving.

        Values:

        - kFrontLeft: front left
        - kFrontRight: front right
        - kRearLeft: rear left
        - kRearRight: rear right
        """
        kFrontLeft = 0
        kFrontRight = 1
        kRearLeft = 2
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

    def __init__(self, *args, **kwargs):
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
        is the motor controller class to use; if unspecified, Talon is used.
        """
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

        if kwargs:
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

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
            raise ValueError("don't know how to handle %d positional arguments" % len(args))

        # convert channel number into motor controller if needed
        cls = kwargs.pop("motorController", Talon)
        if (self.frontLeftMotor is not None and
            not hasattr(self.frontLeftMotor, "set")):
            self.frontLeftMotor = cls(self.frontLeftMotor)
        if (self.rearLeftMotor is not None and
            not hasattr(self.rearLeftMotor, "set")):
            self.rearLeftMotor = cls(self.rearLeftMotor)
        if (self.frontRightMotor is not None and
            not hasattr(self.frontRightMotor, "set")):
            self.frontRightMotor = cls(self.frontRightMotor)
        if (self.rearRightMotor is not None and
            not hasattr(self.rearRightMotor, "set")):
            self.rearRightMotor = cls(self.rearRightMotor)

        # all motors start non-inverted
        self.invertedMotors = [1]*self.kMaxNumberOfMotors

        # other defaults
        self.maxOutput = 1.0
        self.sensitivity = None
        self.isCANInitialized = False #TODO: fix can

        # set up motor safety
        self.setExpiration(self.kDefaultExpirationTime)
        self.setSafetyEnabled(True)

        # start off not moving
        self.drive(0, 0)

    def drive(self, outputMagnitude, curve):
        """Drive the motors at "speed" and "curve".

        The speed and curve are -1.0 to +1.0 values where 0.0 represents
        stopped and not turning. The algorithm for adding in the direction
        attempts to provide a constant turn radius for differing speeds.

        This function will most likely be used in an autonomous routine.

        :param outputMagnitude: The forward component of the output magnitude
            to send to the motors.
        :param curve: The rate of turn, constant for different forward speeds.
        """
        if not RobotDrive.kArcadeRatioCurve_Reported:
            hal.HALReport(hal.HALUsageReporting.kResourceType_RobotDrive,
                          self.getNumMotors(),
                          hal.HALUsageReporting.kRobotDrive_ArcadeRatioCurve)
            RobotDrive.kArcadeRatioCurve_Reported = True
        if curve < 0:
            value = math.log(-curve)
            ratio = (value - self.sensitivity) / (value + self.sensitivity)
            if ratio == 0:
                ratio = .0000000001
            leftOutput = outputMagnitude / ratio
            rightOutput = outputMagnitude
        elif curve > 0:
            value = math.log(curve)
            ratio = (value - self.sensitivity) / (value + self.sensitivity)
            if ratio == 0:
                ratio = .0000000001
            leftOutput = outputMagnitude
            rightOutput = outputMagnitude / ratio
        else:
            leftOutput = outputMagnitude
            rightOutput = outputMagnitude
        self.setLeftRightMotorOutputs(leftOutput, rightOutput)

    def tankDrive(self, *args, **kwargs):
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
        # keyword arguments
        leftStick = kwargs.pop("leftStick", None)
        rightStick = kwargs.pop("rightStick", None)
        leftAxis = kwargs.pop("leftAxis", None)
        rightAxis = kwargs.pop("rightAxis", None)
        leftValue = kwargs.pop("leftValue", None)
        rightValue = kwargs.pop("rightValue", None)
        squaredInputs = kwargs.pop("squaredInputs", None)

        if kwargs:
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

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
        else:
            raise ValueError("invalid number (%d) of positional arguments" % len(args))

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

        # usage reporting
        if not RobotDrive.kTank_Reported:
            hal.HALReport(hal.HALUsageReporting.kResourceType_RobotDrive,
                          self.getNumMotors(),
                          hal.HALUsageReporting.kRobotDrive_Tank)
            RobotDrive.kTank_Reported = True

        # square the inputs (while preserving the sign) to increase fine
        # control while permitting full power
        leftValue = RobotDrive.limit(leftValue)
        rightValue = RobotDrive.limit(rightValue)
        if squaredInputs:
            if leftValue >= 0.0:
                leftValue = (leftValue * leftValue)
            else:
                leftValue = -(leftValue * leftValue)
            if rightValue >= 0.0:
                rightValue = (rightValue * rightValue)
            else:
                rightValue = -(rightValue * rightValue)
        self.setLeftRightMotorOutputs(leftValue, rightValue)

    def arcadeDrive(self, *args, **kwargs):
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
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

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
        else:
            raise ValueError("invalid number (%d) of positional arguments" % len(args))

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
        if not RobotDrive.kArcadeStandard_Reported:
            hal.HALReport(hal.HALUsageReporting.kResourceType_RobotDrive,
                          self.getNumMotors(),
                          hal.HALUsageReporting.kRobotDrive_ArcadeStandard)
            RobotDrive.kArcadeStandard_Reported = True

        moveValue = RobotDrive.limit(moveValue)
        rotateValue = RobotDrive.limit(rotateValue)

        if squaredInputs:
            # square the inputs (while preserving the sign) to increase fine
            # control while permitting full power
            if moveValue >= 0.0:
                moveValue = (moveValue * moveValue)
            else:
                moveValue = -(moveValue * moveValue)
            if rotateValue >= 0.0:
                rotateValue = (rotateValue * rotateValue)
            else:
                rotateValue = -(rotateValue * rotateValue)

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

    def mecanumDrive_Cartesian(self, x, y, rotation, gyroAngle):
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
            hal.HALReport(hal.HALUsageReporting.kResourceType_RobotDrive,
                          self.getNumMotors(),
                          hal.HALUsageReporting.kRobotDrive_MecanumCartesian)
            RobotDrive.kMecanumCartesian_Reported = True
        xIn = x
        yIn = y
        # Negate y for the joystick.
        yIn = -yIn
        # Compenstate for gyro angle.
        xIn, yIn = RobotDrive.rotateVector(xIn, yIn, gyroAngle)

        wheelSpeeds = [0]*self.kMaxNumberOfMotors
        wheelSpeeds[self.MotorType.kFrontLeft] = xIn + yIn + rotation
        wheelSpeeds[self.MotorType.kFrontRight] = -xIn + yIn - rotation
        wheelSpeeds[self.MotorType.kRearLeft] = -xIn + yIn + rotation
        wheelSpeeds[self.MotorType.kRearRight] = xIn + yIn - rotation

        RobotDrive.normalize(wheelSpeeds)

        syncGroup = 0x80

        self.frontLeftMotor.set(wheelSpeeds[self.MotorType.kFrontLeft] * self.invertedMotors[self.MotorType.kFrontLeft] * self.maxOutput, syncGroup)
        self.frontRightMotor.set(wheelSpeeds[self.MotorType.kFrontRight] * self.invertedMotors[self.MotorType.kFrontRight] * self.maxOutput, syncGroup)
        self.rearLeftMotor.set(wheelSpeeds[self.MotorType.kRearLeft] * self.invertedMotors[self.MotorType.kRearLeft] * self.maxOutput, syncGroup)
        self.rearRightMotor.set(wheelSpeeds[self.MotorType.kRearRight] * self.invertedMotors[self.MotorType.kRearRight] * self.maxOutput, syncGroup)

        if self.isCANInitialized:
            pass
            # TODO
            #try:
            #    CANJaguar.updateSyncGroup(syncGroup)
            #except CANNotInitializedException:
            #    self.isCANInitialized = False

        self.feed()

    def mecanumDrive_Polar(self, magnitude, direction, rotation):
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
            hal.HALReport(hal.HALUsageReporting.kResourceType_RobotDrive,
                          self.getNumMotors(),
                          hal.HALUsageReporting.kRobotDrive_MecanumPolar)
            RobotDrive.kMecanumPolar_Reported = True
        # Normalized for full power along the Cartesian axes.
        magnitude = limit(magnitude) * math.sqrt(2.0)
        # The rollers are at 45 degree angles.
        dirInRad = math.radians(direction + 45.0)
        cosD = math.cos(dirInRad)
        sinD = math.sin(dirInRad)

        wheelSpeeds = [0]*self.kMaxNumberOfMotors
        wheelSpeeds[self.MotorType.kFrontLeft] = sinD * magnitude + rotation
        wheelSpeeds[self.MotorType.kFrontRight] = cosD * magnitude - rotation
        wheelSpeeds[self.MotorType.kRearLeft] = cosD * magnitude + rotation
        wheelSpeeds[self.MotorType.kRearRight] = sinD * magnitude - rotation

        RobotDrive.normalize(wheelSpeeds)

        syncGroup = 0x80

        self.frontLeftMotor.set(wheelSpeeds[self.MotorType.kFrontLeft] * self.invertedMotors[self.MotorType.kFrontLeft] * self.maxOutput, syncGroup)
        self.frontRightMotor.set(wheelSpeeds[self.MotorType.kFrontRight] * self.invertedMotors[self.MotorType.kFrontRight] * self.maxOutput, syncGroup)
        self.rearLeftMotor.set(wheelSpeeds[self.MotorType.kRearLeft] * self.invertedMotors[self.MotorType.kRearLeft] * self.maxOutput, syncGroup)
        self.rearRightMotor.set(wheelSpeeds[self.MotorType.kRearRight] * self.invertedMotors[self.MotorType.kRearRight] * self.maxOutput, syncGroup)

        if self.isCANInitialized:
            pass
            # TODO
            #try:
            #    CANJaguar.updateSyncGroup(syncGroup)
            #except CANNotInitializedException:
            #    self.isCANInitialized = False

        self.feed()

    def holonomicDrive(self, magnitude, direction, rotation):
        """Holonomic Drive method for Mecanum wheeled robots.

        This is an alias to :func:`mecanumDrive_Polar` for backward
        compatability.

        :param magnitude: The speed that the robot should drive in a given
            direction.  [-1.0..1.0]
        :param direction: The direction the robot should drive. The direction
            and maginitute are independent of the rotation rate.
        :param rotation: The rate of rotation for the robot that is
            completely independent of the magnitute or direction.  [-1.0..1.0]
        """
        self.mecanumDrive_Polar(magnitude, direction, rotation)

    def setLeftRightMotorOutputs(self, leftOutput, rightOutput):
        """Set the speed of the right and left motors.

        This is used once an appropriate drive setup function is called such as
        twoWheelDrive(). The motors are set to "leftSpeed" and "rightSpeed"
        and includes flipping the direction of one side for opposing motors.

        :param leftOutput: The speed to send to the left side of the robot.
        :param rightOutput: The speed to send to the right side of the robot.
        """
        if self.rearLeftMotor is None or self.rearRightMotor is None:
            raise ValueError("Null motor provided")

        syncGroup = 0x80

        leftOutput = RobotDrive.limit(leftOutput) * self.maxOutput
        rightOutput = RobotDrive.limit(rightOutput) * self.maxOutput

        if self.frontLeftMotor is not None:
            self.frontLeftMotor.set(leftOutput * self.invertedMotors[self.MotorType.kFrontLeft], syncGroup)
        self.rearLeftMotor.set(leftOutput * self.invertedMotors[self.MotorType.kRearLeft], syncGroup)

        if self.frontRightMotor is not None:
            self.frontRightMotor.set(-rightOutput * self.invertedMotors[self.MotorType.kFrontRight], syncGroup)
        self.rearRightMotor.set(-rightOutput * self.invertedMotors[self.MotorType.kRearRight], syncGroup)

        if self.isCANInitialized:
            pass
            # TODO
            #try:
            #    CANJaguar.updateSyncGroup(syncGroup)
            #except CANNotInitializedException:
            #    self.isCANInitialized = False

        self.feed()

    @staticmethod
    def limit(num):
        """Limit motor values to the -1.0 to +1.0 range."""
        if num > 1.0:
            return 1.0
        if num < -1.0:
            return -1.0
        return num

    @staticmethod
    def normalize(wheelSpeeds):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1.0.
        """
        maxMagnitude = abs(wheelSpeeds[0])
        for i in range(1, self.kMaxNumberOfMotors):
            temp = abs(wheelSpeeds[i])
            if maxMagnitude < temp:
                maxMagnitude = temp
        if maxMagnitude > 1.0:
            for i in range(self.kMaxNumberOfMotors):
                wheelSpeeds[i] = wheelSpeeds[i] / maxMagnitude

    @staticmethod
    def rotateVector(x, y, angle):
        """Rotate a vector in Cartesian space."""
        cosA = math.cos(math.radians(angle))
        sinA = math.sin(math.radians(angle))
        return (x * cosA - y * sinA), (x * sinA + y * cosA)

    def setInvertedMotor(self, motor, isInverted):
        """Invert a motor direction.

        This is used when a motor should run in the opposite direction as
        the drive code would normally run it. Motors that are direct drive
        would be inverted, the drive code assumes that the motors are geared
        with one reversal.

        :param motor: The motor index to invert.
        :param isInverted: True if the motor should be inverted when operated.
        """
        self.invertedMotors[motor] = -1 if isInverted else 1

    def setSensitivity(self, sensitivity):
        """Set the turning sensitivity.

        This only impacts the drive() entry-point.

        :param sensitivity: Effectively sets the turning sensitivity (or turn
        radius for a given value)
        """
        self.sensitivity = sensitivity

    def setMaxOutput(self, maxOutput):
        """Configure the scaling factor for using RobotDrive with motor
        controllers in a mode other than PercentVbus.

        :param maxOutput: Multiplied with the output percentage computed by
            the drive functions.
        """
        self.maxOutput = maxOutput


    def getDescription(self):
        return "Robot Drive"

    def stopMotor(self):
        if self.frontLeftMotor is not None:
            self.frontLeftMotor.set(0.0)
        if self.frontRightMotor is not None:
            self.frontRightMotor.set(0.0)
        if self.rearLeftMotor is not None:
            self.rearLeftMotor.set(0.0)
        if self.rearRightMotor is not None:
            self.rearRightMotor.set(0.0)

    def getNumMotors(self):
        motors = 0
        if self.frontLeftMotor is not None: motors += 1
        if self.frontRightMotor is not None: motors += 1
        if self.rearLeftMotor is not None: motors += 1
        if self.rearRightMotor is not None: motors += 1
        return motors
