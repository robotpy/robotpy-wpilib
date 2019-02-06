import pytest
from unittest.mock import MagicMock
import math


def test_init_diffdrive(wpimock, halmock):
    halmock.getFPGATime.return_value = 1000
    halmock.getLoopTiming.return_value = (
        wpimock.SensorUtil.kSystemClockTicksPerMicrosecond
    )

    left = MagicMock()
    right = MagicMock()

    assert wpimock.drive.DifferentialDrive.instances == 0

    drive = wpimock.drive.DifferentialDrive(left, right)

    assert wpimock.drive.DifferentialDrive.instances == 1
    assert drive.maxOutput == wpimock.drive.RobotDriveBase.kDefaultMaxOutput
    assert drive.deadband == wpimock.drive.RobotDriveBase.kDefaultDeadband

    # TODO: test hal.setPWM() outputs


def test_init_killough(wpimock, halmock):
    halmock.getFPGATime.return_value = 1000
    halmock.getLoopTiming.return_value = (
        wpimock.SensorUtil.kSystemClockTicksPerMicrosecond
    )

    left = MagicMock()
    right = MagicMock()
    back = MagicMock()

    assert wpimock.drive.KilloughDrive.instances == 0

    drive = wpimock.drive.KilloughDrive(left, right, back)

    assert wpimock.drive.KilloughDrive.instances == 1
    assert drive.maxOutput == wpimock.drive.RobotDriveBase.kDefaultMaxOutput
    assert drive.deadband == wpimock.drive.RobotDriveBase.kDefaultDeadband

    assert drive.leftMotor == left
    assert drive.rightMotor == right
    assert drive.backMotor == back

    # TODO: test hal.setPWM() outputs


def test_init_mecanum(wpimock, halmock):
    halmock.getFPGATime.return_value = 1000
    halmock.getLoopTiming.return_value = (
        wpimock.SensorUtil.kSystemClockTicksPerMicrosecond
    )

    fleft = MagicMock()
    fright = MagicMock()
    rleft = MagicMock()
    rright = MagicMock()

    assert wpimock.drive.MecanumDrive.instances == 0

    drive = wpimock.drive.MecanumDrive(fleft, rleft, fright, rright)

    assert wpimock.drive.MecanumDrive.instances == 1
    assert drive.frontLeftMotor == fleft
    assert drive.rearLeftMotor == rleft
    assert drive.frontRightMotor == fright
    assert drive.rearRightMotor == rright

    assert drive.maxOutput == wpimock.drive.RobotDriveBase.kDefaultMaxOutput
    assert drive.deadband == wpimock.drive.RobotDriveBase.kDefaultDeadband


def test_init_error(wpimock, halmock):
    halmock.getFPGATime.return_value = 1000

    with pytest.raises(TypeError):
        wpimock.drive.DifferentialDrive()
    with pytest.raises(TypeError):
        wpimock.drive.KilloughDrive()
    with pytest.raises(TypeError):
        wpimock.drive.MecanumDrive()


def test_differential_initSendable(wpilib, sendablebuilder):
    m1, m2 = MagicMock(), MagicMock()
    drive = wpilib.drive.DifferentialDrive(m1, m2)
    m1.get.return_value = 0.4
    m2.get.return_value = 0.5
    drive.initSendable(sendablebuilder)
    sendablebuilder.updateTable()
    table = sendablebuilder.getTable()
    assert table.getString(".type", "") == "DifferentialDrive"
    assert table.getBoolean(".actuator", None) == True
    assert table.getNumber("Left Motor Speed", None) == 0.4
    assert table.getNumber("Right Motor Speed", None) == -0.5


def test_differential_initSendable2(wpilib, sendablebuilder):
    m1, m2 = MagicMock(), MagicMock()
    drive = wpilib.drive.DifferentialDrive(m1, m2)
    drive.setRightSideInverted(False)
    m1.get.return_value = 0.4
    m2.get.return_value = 0.5
    drive.initSendable(sendablebuilder)
    sendablebuilder.updateTable()
    table = sendablebuilder.getTable()
    assert table.getString(".type", "") == "DifferentialDrive"
    assert table.getBoolean(".actuator", None) == True
    assert table.getNumber("Left Motor Speed", None) == 0.4
    assert table.getNumber("Right Motor Speed", None) == 0.5


def test_killough_initSendable(wpilib, sendablebuilder):
    m1, m2, m3 = [MagicMock() for x in range(3)]
    drive = wpilib.drive.KilloughDrive(m1, m2, m3)
    m1.get.return_value = 0.4
    m2.get.return_value = 0.5
    m3.get.return_value = -0.7
    drive.initSendable(sendablebuilder)
    sendablebuilder.updateTable()
    table = sendablebuilder.getTable()
    assert table.getString(".type", "") == "KilloughDrive"
    assert table.getBoolean(".actuator", None) == True
    assert table.getNumber("Left Motor Speed", None) == 0.4
    assert table.getNumber("Right Motor Speed", None) == 0.5
    assert table.getNumber("Back Motor Speed", None) == -0.7


def test_mechanum_initSendable(wpilib, sendablebuilder):
    m1, m2, m3, m4 = [MagicMock() for x in range(4)]
    drive = wpilib.drive.MecanumDrive(m1, m2, m3, m4)
    m1.get.return_value = 0.4
    m2.get.return_value = 0.5
    m3.get.return_value = -0.7
    m4.get.return_value = -0.8
    drive.initSendable(sendablebuilder)
    sendablebuilder.updateTable()
    table = sendablebuilder.getTable()
    assert table.getString(".type", "") == "MecanumDrive"
    assert table.getBoolean(".actuator", None) == True
    assert table.getNumber("Front Left Motor Speed", None) == 0.4
    assert table.getNumber("Front Right Motor Speed", None) == 0.7
    assert table.getNumber("Rear Left Motor Speed", None) == 0.5
    assert table.getNumber("Rear Right Motor Speed", None) == 0.8


def test_mechanum_initSendable2(wpilib, sendablebuilder):
    m1, m2, m3, m4 = [MagicMock() for x in range(4)]
    drive = wpilib.drive.MecanumDrive(m1, m2, m3, m4)
    drive.setRightSideInverted(False)
    m1.get.return_value = 0.4
    m2.get.return_value = 0.5
    m3.get.return_value = -0.7
    m4.get.return_value = -0.8
    drive.initSendable(sendablebuilder)
    sendablebuilder.updateTable()
    table = sendablebuilder.getTable()
    assert table.getString(".type", "") == "MecanumDrive"
    assert table.getBoolean(".actuator", None) == True
    assert table.getNumber("Front Left Motor Speed", None) == 0.4
    assert table.getNumber("Front Right Motor Speed", None) == -0.7
    assert table.getNumber("Rear Left Motor Speed", None) == 0.5
    assert table.getNumber("Rear Right Motor Speed", None) == -0.8


@pytest.fixture(scope="function")
def drive_diff(wpimock, halmock):
    """Left/right drive (mocks out setLeftRightMotorOutputs)."""
    halmock.getFPGATime.return_value = 1000
    left = MagicMock()
    right = MagicMock()
    drive = wpimock.drive.DifferentialDrive(left, right)
    drive.leftMotor.set = MagicMock()
    drive.rightMotor.set = MagicMock()
    left.reset_mock()
    right.reset_mock()
    return drive


@pytest.fixture(scope="function")
def drive_killough(wpimock, halmock):
    """Killough drive"""
    halmock.getFPGATime.return_value = 1000
    m1 = MagicMock()
    m2 = MagicMock()
    m3 = MagicMock()
    drive = wpimock.drive.KilloughDrive(m1, m2, m3)
    drive._test_motors = [m1, m2, m3]  # ordered by MotorType
    m1.reset_mock()
    m2.reset_mock()
    m3.reset_mock()
    return drive


@pytest.fixture(scope="function")
def drive_mecanum(wpimock, halmock):
    """Killough drive"""
    halmock.getFPGATime.return_value = 1000
    m1 = MagicMock()
    m2 = MagicMock()
    m3 = MagicMock()
    m4 = MagicMock()
    drive = wpimock.drive.MecanumDrive(m1, m2, m3, m4)
    drive._test_motors = [m1, m3, m2, m4]  # ordered by MotorType
    m1.reset_mock()
    m2.reset_mock()
    m3.reset_mock()
    m4.reset_mock()
    return drive


def check_curvature(wpimock, drive_diff, y, rotation, isQuickTurn):
    quickStopAccumulator = 0
    y = wpimock.drive.RobotDriveBase.limit(y)
    y = wpimock.drive.RobotDriveBase.applyDeadband(y, drive_diff.deadband)

    rotation = wpimock.drive.RobotDriveBase.limit(rotation)
    rotation = wpimock.drive.RobotDriveBase.applyDeadband(rotation, drive_diff.deadband)

    if isQuickTurn:
        if abs(y) < drive_diff.quickStopThreshold:
            quickStopAccumulator = (
                (1 - drive_diff.quickStopAlpha) * quickStopAccumulator
                + drive_diff.quickStopAlpha
                * wpimock.drive.RobotDriveBase.limit(rotation)
                * 2
            )

        overPower = True
        angularPower = rotation

    else:
        overPower = False
        angularPower = abs(y) * rotation - quickStopAccumulator

        if quickStopAccumulator > 1:
            quickStopAccumulator -= 1
        elif quickStopAccumulator < -1:
            quickStopAccumulator += 1
        else:
            quickStopAccumulator = 0

    leftMotorSpeed = y + angularPower
    rightMotorSpeed = y - angularPower

    if overPower:
        if leftMotorSpeed > 1.0:
            rightMotorSpeed -= leftMotorSpeed - 1.0
            leftMotorSpeed = 1.0
        elif rightMotorSpeed > 1.0:
            leftMotorSpeed -= rightMotorSpeed - 1.0
            rightMotorSpeed = 1.0
        elif leftMotorSpeed < -1.0:
            rightMotorSpeed -= leftMotorSpeed + 1.0
            leftMotorSpeed = -1.0
        elif rightMotorSpeed < -1.0:
            leftMotorSpeed -= rightMotorSpeed + 1.0
            rightMotorSpeed = -1.0

    maxMagnitude = max(abs(leftMotorSpeed), abs(rightMotorSpeed))
    if maxMagnitude > 1.0:
        leftMotorSpeed /= maxMagnitude
        rightMotorSpeed /= maxMagnitude

    drive_diff.leftMotor.set.assert_called_once_with(
        leftMotorSpeed * drive_diff.maxOutput
    )
    drive_diff.rightMotor.set.assert_called_once_with(
        -rightMotorSpeed * drive_diff.maxOutput
    )


# fmt: off
@pytest.mark.parametrize("y,rotation,isQuickTurn",
                         [(0.0, 0.0, False),
                          (0.001, math.e ** 0.5, False), (0.001, -math.e ** 0.5, False),  # hit ratio==0 case
                          (-0.5, 0.0, False), (-1.0, 0.0, False), (0.5, 0.0, False), (1.0, 0.0, False),
                          (0.0, -0.5, False), (0.0, -1.0, False), (0.0, 0.5, False), (0.0, 1.0, False),
                          (-0.5, -0.5, False), (-0.5, -1.0, False), (-0.5, 0.5, False), (-0.5, 1.0, False),
                          (0.5, -0.5, False), (0.5, -1.0, False), (0.5, 0.5, False), (0.5, 1.0, False),
                          (0.0, 0.0, True), (0.001, math.e ** 0.5, True), (0.001, -math.e ** 0.5, True),
                          # hit ratio==0 case
                          (-0.5, 0.0, True), (-1.0, 0.0, True), (0.5, 0.0, True), (1.0, 0.0, True),
                          (0.0, -0.5, True), (0.0, -1.0, True), (0.0, 0.5, True), (0.0, 1.0, True),
                          (-0.5, -0.5, True), (-0.5, -1.0, True), (-0.5, 0.5, True), (-0.5, 1.0, True),
                          (0.5, -0.5, True), (0.5, -1.0, True), (0.5, 0.5, True), (0.5, 1.0, True)])
def test_drive(y, rotation, isQuickTurn, drive_diff, wpimock):
    # left, right calculation
    drive_diff.curvatureDrive(y, rotation, isQuickTurn)
    check_curvature(wpimock, drive_diff, y, rotation, isQuickTurn)
# fmt: on


def check_tank(wpimock, drive_diff, lv, rv, sq):
    lv = wpimock.drive.RobotDriveBase.limit(lv)
    lv = wpimock.drive.RobotDriveBase.applyDeadband(lv, drive_diff.deadband)
    rv = wpimock.drive.RobotDriveBase.limit(rv)
    rv = wpimock.drive.RobotDriveBase.applyDeadband(rv, drive_diff.deadband)

    if sq:
        lv = math.copysign(lv * lv, lv)
        rv = math.copysign(rv * rv, rv)
    drive_diff.leftMotor.set.assert_called_once_with(lv)
    drive_diff.rightMotor.set.assert_called_once_with(-rv)


@pytest.mark.parametrize(
    "sq,lv,rv",
    [
        (False, 0.3, -0.3),
        (True, -0.3, 0.3),
        (None, 0.3, -0.3),
        (False, -0.3, 0.3),
        (True, 0.3, -0.3),
        (None, -0.3, 0.3),
    ],
)
def test_tankDrive_value(wpimock, sq, lv, rv, drive_diff):
    drive_diff.tankDrive(lv, rv, sq)
    check_tank(wpimock, drive_diff, lv, rv, sq)


def test_tankDrive_error(drive_diff):
    with pytest.raises(TypeError):
        drive_diff.tankDrive()
    with pytest.raises(TypeError):
        drive_diff.tankDrive(1.0)


def check_arcade(wpimock, drive_diff, y, rotation, sq):
    y = wpimock.drive.RobotDriveBase.limit(y)
    y = wpimock.drive.RobotDriveBase.applyDeadband(y, drive_diff.deadband)

    rotation = wpimock.drive.RobotDriveBase.limit(rotation)
    rotation = wpimock.drive.RobotDriveBase.applyDeadband(rotation, drive_diff.deadband)

    if sq:
        # square the inputs (while preserving the sign) to increase fine
        # control while permitting full power
        y = math.copysign(y * y, y)
        rotation = math.copysign(rotation * rotation, rotation)

    maxInput = math.copysign(max(abs(y), abs(rotation)), y)

    if y > 0.0:
        if rotation > 0.0:
            leftMotorSpeed = maxInput
            rightMotorSpeed = y - rotation
        else:
            leftMotorSpeed = y + rotation
            rightMotorSpeed = maxInput
    else:
        if rotation > 0.0:
            leftMotorSpeed = y + rotation
            rightMotorSpeed = maxInput
        else:
            leftMotorSpeed = maxInput
            rightMotorSpeed = y - rotation
    drive_diff.leftMotor.set.assert_called_once_with(
        leftMotorSpeed * drive_diff.maxOutput
    )
    drive_diff.rightMotor.set.assert_called_once_with(
        -rightMotorSpeed * drive_diff.maxOutput
    )


@pytest.mark.parametrize(
    "sq,y,rotation",
    [
        (False, 0.3, -0.3),
        (True, -0.3, 0.3),
        (None, 0.3, -0.3),
        (False, -0.3, 0.3),
        (True, 0.3, -0.3),
        (None, -0.3, 0.3),
    ],
)
def test_arcadeDrive_value(wpimock, sq, y, rotation, drive_diff):
    drive_diff.arcadeDrive(y, rotation, sq)
    check_arcade(wpimock, drive_diff, y, rotation, sq)


def test_arcadeDrive_error(drive_diff):
    with pytest.raises(TypeError):
        drive_diff.arcadeDrive()
    with pytest.raises(TypeError):
        drive_diff.arcadeDrive(1.0)
    with pytest.raises(TypeError):
        drive_diff.arcadeDrive(1, 1, 1, 1, 1, 1)


def test_real_diff_curvature(wpilib):
    drive_diff = wpilib.drive.DifferentialDrive(wpilib.Spark(0), wpilib.Spark(1))
    drive_diff.curvatureDrive(1, 0.25, False)
    drive_diff.curvatureDrive(-1, -1, True)


def test_mecanumDrive_Cartesian(drive_mecanum):
    drive_mecanum.driveCartesian(0.3, 0.4, -0.2, -20)
    # TODO: check values
    assert drive_mecanum.frontLeftMotor.set.called
    assert drive_mecanum.rearLeftMotor.set.called
    assert drive_mecanum.frontRightMotor.set.called
    assert drive_mecanum.rearRightMotor.set.called


def test_mecanumDrive_Polar(drive_mecanum):
    drive_mecanum.drivePolar(0.3, 20, -0.4)
    # TODO: check values
    assert drive_mecanum.frontLeftMotor.set.called
    assert drive_mecanum.rearLeftMotor.set.called
    assert drive_mecanum.frontRightMotor.set.called
    assert drive_mecanum.rearRightMotor.set.called


@pytest.mark.parametrize(
    "val,result", [(1.1, 1.0), (-1.1, -1.0), (0.9, 0.9), (-0.9, -0.9)]
)
def test_limit(val, result, wpimock):
    assert wpimock.drive.RobotDriveBase.limit(val) == result


@pytest.mark.parametrize(
    "val,result",
    [
        ((0.6, -0.7, 0.8, 0.9), (0.6, -0.7, 0.8, 0.9)),
        ((2.0, 1.0, -1.0, 0.5), (1.0, 0.5, -0.5, 0.25)),
        ((-2.0, -0.5, 0.0, 1.0), (-1.0, -0.25, 0.0, 0.5)),
    ],
)
def test_normalize(val, result, wpimock):
    speeds = list(val)
    wpimock.drive.RobotDriveBase.normalize(speeds)
    assert tuple(speeds) == result


@pytest.mark.parametrize("angle", [-30, 0, 30])
def test_rotateVector(angle, wpimock):
    x = 0.6
    y = 0.7
    cosA = math.cos(math.radians(angle))
    sinA = math.sin(math.radians(angle))

    vector = wpimock.drive.Vector2d(x, y)
    vector.rotate(angle)
    assert (vector.x, vector.y) == ((x * cosA - y * sinA), (x * sinA + y * cosA))


def test_setMaxOutput(drive_diff):
    drive_diff.setMaxOutput(0.5)
    drive_diff.setDeadband(0)
    assert drive_diff.maxOutput == 0.5
    # drive to make sure it took effect
    drive_diff.tankDrive(1.0, 0.75, squareInputs=False)
    drive_diff.leftMotor.set.assert_called_once_with(0.5)
    drive_diff.rightMotor.set.assert_called_once_with(-0.375)


@pytest.mark.parametrize("r_inverted, expected_r_output", [(True, -1.0), (False, 1.0)])
def test_setRightSideInverted_tank(drive_diff, r_inverted, expected_r_output):
    drive_diff.setDeadband(0)
    drive_diff.setRightSideInverted(r_inverted)
    assert drive_diff.isRightSideInverted() == r_inverted
    drive_diff.tankDrive(1.0, 1.0, squareInputs=False)
    drive_diff.leftMotor.set.assert_called_once_with(1.0)
    drive_diff.rightMotor.set.assert_called_once_with(expected_r_output)


@pytest.mark.parametrize("r_inverted, expected_r_output", [(True, -1.0), (False, 1.0)])
def test_setRightSideInverted_arcade(drive_diff, r_inverted, expected_r_output):
    drive_diff.setDeadband(0)
    drive_diff.setRightSideInverted(r_inverted)
    assert drive_diff.isRightSideInverted() == r_inverted
    drive_diff.arcadeDrive(1.0, 0, squareInputs=False)
    drive_diff.leftMotor.set.assert_called_once_with(1.0)
    drive_diff.rightMotor.set.assert_called_once_with(expected_r_output)


def test_getDescription(drive_diff, drive_killough, drive_mecanum):
    assert drive_diff.getDescription() == "Differential Drive"
    assert drive_killough.getDescription() == "Killough Drive"
    assert drive_mecanum.getDescription() == "Mecanum Drive"


def test_stopMotor(drive_diff):
    drive_diff.stopMotor()
    drive_diff.leftMotor.stopMotor.assert_called_once_with()
    drive_diff.rightMotor.stopMotor.assert_called_once_with()


def test_stopMotor_4(drive_mecanum):
    drive_mecanum.stopMotor()
    drive_mecanum.frontLeftMotor.stopMotor.assert_called_once_with()
    drive_mecanum.frontRightMotor.stopMotor.assert_called_once_with()
    drive_mecanum.rearLeftMotor.stopMotor.assert_called_once_with()
    drive_mecanum.rearRightMotor.stopMotor.assert_called_once_with()


def test_feedWatchdog(drive_diff):
    drive_diff.feedWatchdog()


def test_killough_driveCartesian(wpilib):
    m1, m2, m3 = MagicMock(), MagicMock(), MagicMock()
    drive = wpilib.drive.KilloughDrive(m1, m2, m3)

    drive.driveCartesian(0.5, 0.5, 0.5, 90)

    m1.set.assert_called_with(pytest.approx(0.566, 0.01))
    m2.set.assert_called_with(pytest.approx(1.0, 0.01))
    m3.set.assert_called_with(pytest.approx(-0.025, 0.01))


def test_killough_drivePolar(wpilib):
    m1, m2, m3 = MagicMock(), MagicMock(), MagicMock()
    drive = wpilib.drive.KilloughDrive(m1, m2, m3)

    drive.drivePolar(0.5, 80, 110)

    m1.set.assert_called_with(pytest.approx(1.0, 0.01))
    m2.set.assert_called_with(pytest.approx(0.998, 0.01))
    m3.set.assert_called_with(pytest.approx(0.987, 0.01))
