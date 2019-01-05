import pytest
from unittest.mock import MagicMock
import math

pytestmark = pytest.mark.filterwarnings("ignore:RobotDrive :DeprecationWarning")


@pytest.mark.parametrize(
    "kw,mc",
    [
        (False, None),
        (False, ""),
        (False, "Victor"),
        (True, None),
        (True, ""),
        (True, "Victor"),
    ],
)
def test_init_two(kw, mc, wpimock, halmock):
    halmock.getFPGATime.return_value = 1000
    halmock.getLoopTiming.return_value = (
        wpimock.SensorUtil.kSystemClockTicksPerMicrosecond
    )

    if mc is None:
        left = MagicMock()
        right = MagicMock()
    else:
        left = 1
        right = 2

    if kw:
        if mc:
            drive = wpimock.RobotDrive(
                leftMotor=left, rightMotor=right, motorController=getattr(wpimock, mc)
            )
        else:
            drive = wpimock.RobotDrive(leftMotor=left, rightMotor=right)
    else:
        if mc:
            drive = wpimock.RobotDrive(
                left, right, motorController=getattr(wpimock, mc)
            )
        else:
            drive = wpimock.RobotDrive(left, right)

    assert drive.maxOutput == wpimock.RobotDrive.kDefaultMaxOutput
    assert drive.sensitivity == wpimock.RobotDrive.kDefaultSensitivity
    assert drive._MotorSafety__enabled

    assert drive.frontLeftMotor is None
    assert drive.frontRightMotor is None
    if mc is None:
        assert drive.rearLeftMotor == left
        assert drive.rearRightMotor == right

        left.set.assert_called_once_with(0.0)
        right.set.assert_called_once_with(0.0)
    else:
        if mc:
            mclass = getattr(wpimock, mc)
        else:
            mclass = wpimock.Talon
        assert isinstance(drive.rearLeftMotor, mclass)
        assert isinstance(drive.rearRightMotor, mclass)
        assert drive.rearLeftMotor.getChannel() == left
        assert drive.rearRightMotor.getChannel() == right
        # TODO: test hal.setPWM() outputs


@pytest.mark.parametrize(
    "kw,mc",
    [
        (False, None),
        (False, ""),
        (False, "Victor"),
        (True, None),
        (True, ""),
        (True, "Victor"),
    ],
)
def test_init_four(kw, mc, wpimock, halmock):
    halmock.getFPGATime.return_value = 1000
    halmock.getLoopTiming.return_value = (
        wpimock.SensorUtil.kSystemClockTicksPerMicrosecond
    )

    if mc is None:
        fleft = MagicMock()
        rleft = MagicMock()
        fright = MagicMock()
        rright = MagicMock()
    else:
        fleft = 1
        rleft = 2
        fright = 3
        rright = 4

    if kw:
        if mc:
            drive = wpimock.RobotDrive(
                frontLeftMotor=fleft,
                rearLeftMotor=rleft,
                frontRightMotor=fright,
                rearRightMotor=rright,
                motorController=getattr(wpimock, mc),
            )
        else:
            drive = wpimock.RobotDrive(
                frontLeftMotor=fleft,
                rearLeftMotor=rleft,
                frontRightMotor=fright,
                rearRightMotor=rright,
            )
    else:
        if mc:
            drive = wpimock.RobotDrive(
                fleft, rleft, fright, rright, motorController=getattr(wpimock, mc)
            )
        else:
            drive = wpimock.RobotDrive(fleft, rleft, fright, rright)

    assert drive.maxOutput == wpimock.RobotDrive.kDefaultMaxOutput
    assert drive.sensitivity == wpimock.RobotDrive.kDefaultSensitivity
    assert drive._MotorSafety__enabled

    if mc is None:
        assert drive.frontLeftMotor == fleft
        assert drive.rearLeftMotor == rleft
        assert drive.frontRightMotor == fright
        assert drive.rearRightMotor == rright

        fleft.set.assert_called_once_with(0.0)
        rleft.set.assert_called_once_with(0.0)
        fright.set.assert_called_once_with(0.0)
        rright.set.assert_called_once_with(0.0)
    else:
        if mc:
            mclass = getattr(wpimock, mc)
        else:
            mclass = wpimock.Talon
        assert isinstance(drive.frontLeftMotor, mclass)
        assert isinstance(drive.rearLeftMotor, mclass)
        assert isinstance(drive.frontRightMotor, mclass)
        assert isinstance(drive.rearRightMotor, mclass)
        assert drive.frontLeftMotor.getChannel() == fleft
        assert drive.rearLeftMotor.getChannel() == rleft
        assert drive.frontRightMotor.getChannel() == fright
        assert drive.rearRightMotor.getChannel() == rright
        # TODO: test hal.setPWM() outputs


def test_init_error(wpimock, halmock):
    halmock.getFPGATime.return_value = 1000

    with pytest.raises(ValueError):
        wpimock.RobotDrive()
    with pytest.raises(ValueError):
        wpimock.RobotDrive(1)


def test_init_warning(wpimock, halmock, recwarn):
    halmock.getFPGATime.return_value = 1000
    wpimock.RobotDrive(MagicMock(), MagicMock(), foo=5)
    w = recwarn.pop(RuntimeWarning)
    assert issubclass(w.category, RuntimeWarning)
    assert "foo" in str(w.message)


@pytest.fixture(scope="function")
def drive_lr(wpimock, halmock):
    """Left/right drive (mocks out setLeftRightMotorOutputs)."""
    halmock.getFPGATime.return_value = 1000
    left = MagicMock()
    right = MagicMock()
    drive = wpimock.RobotDrive(left, right)
    drive.setLeftRightMotorOutputs = MagicMock()
    left.reset_mock()
    right.reset_mock()
    return drive


@pytest.fixture(scope="function")
def drive4(wpimock, halmock):
    """4-motor drive"""
    halmock.getFPGATime.return_value = 1000
    m1 = MagicMock()
    m2 = MagicMock()
    m3 = MagicMock()
    m4 = MagicMock()
    drive = wpimock.RobotDrive(m1, m2, m3, m4)
    drive._test_motors = [m1, m3, m2, m4]  # ordered by MotorType
    m1.reset_mock()
    m2.reset_mock()
    m3.reset_mock()
    m4.reset_mock()
    return drive


def check_drive(drive_lr, mag, curve):
    sensitivity = drive_lr.sensitivity
    if curve < 0:
        value = math.log(-curve)
        ratio = (value - sensitivity) / (value + sensitivity)
        if ratio == 0:
            ratio = 0.0000000001
        left = mag / ratio
        right = mag
    elif curve > 0:
        value = math.log(curve)
        ratio = (value - sensitivity) / (value + sensitivity)
        if ratio == 0:
            ratio = 0.0000000001
        left = mag
        right = mag / ratio
    else:
        left = mag
        right = mag
    drive_lr.setLeftRightMotorOutputs.assert_called_once_with(left, right)


@pytest.mark.parametrize(
    "mag,curve",
    [
        (0.0, 0.0),
        (0.001, math.e ** 0.5),
        (0.001, -math.e ** 0.5),  # hit ratio==0 case
        (-0.5, 0.0),
        (-1.0, 0.0),
        (0.5, 0.0),
        (1.0, 0.0),
        (0.0, -0.5),
        (0.0, -1.0),
        (0.0, 0.5),
        (0.0, 1.0),
        (-0.5, -0.5),
        (-0.5, -1.0),
        (-0.5, 0.5),
        (-0.5, 1.0),
        (0.5, -0.5),
        (0.5, -1.0),
        (0.5, 0.5),
        (0.5, 1.0),
    ],
)
def test_drive(mag, curve, drive_lr):
    # left, right calculation
    drive_lr.drive(mag, curve)
    check_drive(drive_lr, mag, curve)


def check_tank(drive_lr, lv, rv, sq):
    if sq is None or sq:
        if lv >= 0.0:
            lv = lv * lv
        else:
            lv = -(lv * lv)
        if rv >= 0.0:
            rv = rv * rv
        else:
            rv = -(rv * rv)
    drive_lr.setLeftRightMotorOutputs.assert_called_once_with(lv, rv)


@pytest.mark.parametrize(
    "kw,sq,axis,lv,rv",
    [
        (False, False, False, 0.3, -0.3),
        (False, False, True, -0.3, 0.3),
        (False, True, False, -0.3, 0.3),
        (False, True, True, 0.3, -0.3),
        (False, None, False, 0.3, -0.3),
        (False, None, True, -0.3, 0.3),
        (True, False, False, -0.3, 0.3),
        (True, False, True, 0.3, -0.3),
        (True, True, False, 0.3, -0.3),
        (True, True, True, -0.3, 0.3),
        (True, None, False, -0.3, 0.3),
        (True, None, True, 0.3, -0.3),
    ],
)
def test_tankDrive_stick(kw, sq, axis, lv, rv, drive_lr):
    leftStick = MagicMock()
    rightStick = MagicMock()
    if axis:
        leftStick.getRawAxis.return_value = lv
        rightStick.getRawAxis.return_value = rv
    else:
        leftStick.getY.return_value = lv
        rightStick.getY.return_value = rv

    if kw:
        kwargs = dict(leftStick=leftStick, rightStick=rightStick)
        if sq is not None:
            kwargs["squaredInputs"] = sq
        if axis:
            kwargs["leftAxis"] = 2
            kwargs["rightAxis"] = 3
        drive_lr.tankDrive(**kwargs)
    else:
        if sq is not None:
            if axis:
                drive_lr.tankDrive(leftStick, 2, rightStick, 3, sq)
            else:
                drive_lr.tankDrive(leftStick, rightStick, sq)
        else:
            if axis:
                drive_lr.tankDrive(leftStick, 2, rightStick, 3)
            else:
                drive_lr.tankDrive(leftStick, rightStick)

    if axis:
        leftStick.getRawAxis.assert_called_once_with(2)
        rightStick.getRawAxis.assert_called_once_with(3)
    check_tank(drive_lr, lv, rv, sq)


@pytest.mark.parametrize(
    "kw,sq,lv,rv",
    [
        (False, False, 0.3, -0.3),
        (False, True, -0.3, 0.3),
        (False, None, 0.3, -0.3),
        (True, False, -0.3, 0.3),
        (True, True, 0.3, -0.3),
        (True, None, -0.3, 0.3),
    ],
)
def test_tankDrive_value(kw, sq, lv, rv, drive_lr):
    if kw:
        kwargs = dict(leftValue=lv, rightValue=rv)
        if sq is not None:
            kwargs["squaredInputs"] = sq
        drive_lr.tankDrive(**kwargs)
    else:
        if sq is not None:
            drive_lr.tankDrive(lv, rv, sq)
        else:
            drive_lr.tankDrive(lv, rv)

    check_tank(drive_lr, lv, rv, sq)


def test_tankDrive_error(drive_lr):
    with pytest.raises(AttributeError):
        drive_lr.tankDrive()
    with pytest.raises(ValueError):
        drive_lr.tankDrive(1.0)


def test_tankDrive_warning(drive_lr, recwarn):
    drive_lr.tankDrive(0.0, 0.0, foo=5)
    w = recwarn.pop(RuntimeWarning)
    assert issubclass(w.category, RuntimeWarning)
    assert "foo" in str(w.message)


def check_arcade(drive_lr, mv, rv, sq):
    if sq is None or sq:
        if mv >= 0.0:
            mv = mv * mv
        else:
            mv = -(mv * mv)
        if rv >= 0.0:
            rv = rv * rv
        else:
            rv = -(rv * rv)
    if mv > 0.0:
        if rv > 0.0:
            left = mv - rv
            right = max(mv, rv)
        else:
            left = max(mv, -rv)
            right = mv + rv
    else:
        if rv > 0.0:
            left = -max(-mv, rv)
            right = mv + rv
        else:
            left = mv - rv
            right = -max(-mv, -rv)
    drive_lr.setLeftRightMotorOutputs.assert_called_once_with(left, right)


@pytest.mark.parametrize(
    "kw,sq,mv,rv",
    [
        (False, False, 0.3, -0.3),
        (False, True, 0.3, 0.3),
        (False, None, 0.3, -0.3),
        (True, False, -0.3, 0.3),
        (True, True, -0.3, -0.3),
        (True, None, -0.3, 0.3),
    ],
)
def test_arcadeDrive_stick(kw, sq, mv, rv, drive_lr):
    moveStick = MagicMock()
    rotateStick = MagicMock()
    moveStick.getRawAxis.return_value = mv
    rotateStick.getRawAxis.return_value = rv

    if kw:
        kwargs = dict(
            moveStick=moveStick, rotateStick=rotateStick, moveAxis=2, rotateAxis=3
        )
        if sq is not None:
            kwargs["squaredInputs"] = sq
        drive_lr.arcadeDrive(**kwargs)
    else:
        if sq is not None:
            drive_lr.arcadeDrive(moveStick, 2, rotateStick, 3, sq)
        else:
            drive_lr.arcadeDrive(moveStick, 2, rotateStick, 3)

    moveStick.getRawAxis.assert_called_once_with(2)
    rotateStick.getRawAxis.assert_called_once_with(3)
    check_arcade(drive_lr, mv, rv, sq)


@pytest.mark.parametrize(
    "kw,sq,mv,rv",
    [
        (False, False, 0.3, -0.3),
        (False, True, 0.3, 0.3),
        (False, None, 0.3, -0.3),
        (True, False, -0.3, 0.3),
        (True, True, -0.3, -0.3),
        (True, None, -0.3, 0.3),
    ],
)
def test_arcadeDrive_onestick(kw, sq, mv, rv, drive_lr):
    stick = MagicMock()
    stick.getY.return_value = mv
    stick.getX.return_value = rv

    if kw:
        kwargs = dict(stick=stick)
        if sq is not None:
            kwargs["squaredInputs"] = sq
        drive_lr.arcadeDrive(**kwargs)
    else:
        if sq is not None:
            drive_lr.arcadeDrive(stick, sq)
        else:
            drive_lr.arcadeDrive(stick)

    check_arcade(drive_lr, mv, rv, sq)


@pytest.mark.parametrize(
    "kw,sq,mv,rv",
    [
        (False, False, 0.3, -0.3),
        (False, True, -0.3, 0.3),
        (False, None, 0.3, -0.3),
        (True, False, -0.3, 0.3),
        (True, True, 0.3, -0.3),
        (True, None, -0.3, 0.3),
    ],
)
def test_arcadeDrive_value(kw, sq, mv, rv, drive_lr):
    if kw:
        kwargs = dict(moveValue=mv, rotateValue=rv)
        if sq is not None:
            kwargs["squaredInputs"] = sq
        drive_lr.arcadeDrive(**kwargs)
    else:
        if sq is not None:
            drive_lr.arcadeDrive(mv, rv, sq)
        else:
            drive_lr.arcadeDrive(mv, rv)

    check_arcade(drive_lr, mv, rv, sq)


def test_arcadeDrive_error(drive_lr):
    with pytest.raises(AttributeError):
        drive_lr.arcadeDrive()
    with pytest.raises(AttributeError):
        drive_lr.arcadeDrive(1.0)
    with pytest.raises(ValueError):
        drive_lr.arcadeDrive(1, 1, 1, 1, 1, 1)


def test_arcadeDrive_warning(drive_lr, recwarn):
    drive_lr.arcadeDrive(0.0, 0.0, foo=5)
    w = recwarn.pop(RuntimeWarning)
    assert issubclass(w.category, RuntimeWarning)
    assert "foo" in str(w.message)


def test_mecanumDrive_Cartesian(drive4):
    drive4.mecanumDrive_Cartesian(0.3, 0.4, -0.2, -20)
    # TODO: check values
    assert drive4.frontLeftMotor.set.called
    assert drive4.rearLeftMotor.set.called
    assert drive4.frontRightMotor.set.called
    assert drive4.rearRightMotor.set.called


def test_mecanumDrive_Polar(drive4):
    drive4.mecanumDrive_Polar(0.3, 20, -0.4)
    # TODO: check values
    assert drive4.frontLeftMotor.set.called
    assert drive4.rearLeftMotor.set.called
    assert drive4.frontRightMotor.set.called
    assert drive4.rearRightMotor.set.called


def test_holonomicDrive(drive4):
    drive4.mecanumDrive_Polar = MagicMock()
    drive4.holonomicDrive(0.2, 0.3, 0.4)
    drive4.mecanumDrive_Polar.assert_called_once_with(0.2, 0.3, 0.4)


def test_setLeftRightMotorOutputs(drive4):
    drive4.feed = MagicMock()
    drive4.setLeftRightMotorOutputs(0.2, 0.3)
    drive4.frontLeftMotor.set.assert_called_once_with(0.2)
    drive4.rearLeftMotor.set.assert_called_once_with(0.2)
    drive4.frontRightMotor.set.assert_called_once_with(-0.3)
    drive4.rearRightMotor.set.assert_called_once_with(-0.3)
    assert drive4.feed.called

    drive4.frontLeftMotor = None
    drive4.frontRightMotor = None
    drive4.rearLeftMotor.reset_mock()
    drive4.rearRightMotor.reset_mock()
    drive4.setLeftRightMotorOutputs(0.2, 0.3)
    drive4.rearLeftMotor.set.assert_called_once_with(0.2)
    drive4.rearRightMotor.set.assert_called_once_with(-0.3)


@pytest.mark.parametrize("motor", ["rearLeftMotor", "rearRightMotor"])
def test_setLeftRightMotorOutputs_error(motor, drive4):
    setattr(drive4, motor, None)
    with pytest.raises(ValueError):
        drive4.setLeftRightMotorOutputs(0.2, 0.3)


@pytest.mark.parametrize(
    "val,result", [(1.1, 1.0), (-1.1, -1.0), (0.9, 0.9), (-0.9, -0.9)]
)
def test_limit(val, result, wpimock):
    assert wpimock.RobotDrive.limit(val) == result


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
    wpimock.RobotDrive.normalize(speeds)
    assert tuple(speeds) == result


@pytest.mark.parametrize("angle", [-30, 0, 30])
def test_rotateVector(angle, wpimock):
    x = 0.6
    y = 0.7
    cosA = math.cos(math.radians(angle))
    sinA = math.sin(math.radians(angle))
    assert wpimock.RobotDrive.rotateVector(x, y, angle) == (
        (x * cosA - y * sinA),
        (x * sinA + y * cosA),
    )


@pytest.mark.parametrize(
    "motor", ["kFrontLeft", "kFrontRight", "kRearLeft", "kRearRight"]
)
def test_setInvertedMotor(motor, drive4):
    motor_idx = getattr(drive4.MotorType, motor)
    motor_obj = drive4._test_motors[motor_idx]

    drive4.setInvertedMotor(motor_idx, True)
    motor_obj.setInverted.assert_called_once_with(True)
    motor_obj.reset_mock()

    drive4.setInvertedMotor(motor_idx, False)
    motor_obj.setInverted.assert_called_once_with(False)
    motor_obj.reset_mock()


def test_setSensitivity(drive_lr):
    drive_lr.setSensitivity(0.1)
    assert drive_lr.sensitivity == 0.1
    # drive to make sure it took effect
    drive_lr.drive(0.2, 0.3)
    check_drive(drive_lr, 0.2, 0.3)


def test_setMaxOutput(drive4):
    drive4.setMaxOutput(0.5)
    assert drive4.maxOutput == 0.5
    # drive to make sure it took effect
    drive4.setLeftRightMotorOutputs(1.0, 0.75)
    drive4.rearLeftMotor.set.assert_called_once_with(0.5)
    drive4.rearRightMotor.set.assert_called_once_with(-0.375)


def test_getDescription(drive_lr):
    assert drive_lr.getDescription() == "Robot Drive"


def test_stopMotor(drive_lr):
    drive_lr.stopMotor()
    drive_lr.rearLeftMotor.stopMotor.assert_called_once_with()
    drive_lr.rearRightMotor.stopMotor.assert_called_once_with()


def test_stopMotor_4(drive4):
    drive4.stopMotor()
    drive4.frontLeftMotor.stopMotor.assert_called_once_with()
    drive4.frontRightMotor.stopMotor.assert_called_once_with()
    drive4.rearLeftMotor.stopMotor.assert_called_once_with()
    drive4.rearRightMotor.stopMotor.assert_called_once_with()
