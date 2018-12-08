import pytest


def test_Accelerometer_Range(wpilib):
    assert hasattr(wpilib.interfaces.Accelerometer.Range, "k2G")
    assert hasattr(wpilib.interfaces.Accelerometer.Range, "k4G")
    assert hasattr(wpilib.interfaces.Accelerometer.Range, "k8G")
    assert hasattr(wpilib.interfaces.Accelerometer.Range, "k16G")


def test_Accelerometer(wpilib):
    x = wpilib.interfaces.Accelerometer()
    with pytest.raises(NotImplementedError):
        x.setRange(x.Range.k8G)
    with pytest.raises(NotImplementedError):
        x.getX()
    with pytest.raises(NotImplementedError):
        x.getY()
    with pytest.raises(NotImplementedError):
        x.getZ()


def test_Controller(wpilib):
    x = wpilib.interfaces.Controller()
    with pytest.raises(NotImplementedError):
        x.enable()
    with pytest.raises(NotImplementedError):
        x.disable()


def test_CounterBase_EncodingType(wpilib):
    assert hasattr(wpilib.interfaces.CounterBase.EncodingType, "k1X")
    assert hasattr(wpilib.interfaces.CounterBase.EncodingType, "k2X")
    assert hasattr(wpilib.interfaces.CounterBase.EncodingType, "k4X")


def test_CounterBase(wpilib):
    x = wpilib.interfaces.CounterBase()
    with pytest.raises(NotImplementedError):
        x.get()
    with pytest.raises(NotImplementedError):
        x.reset()
    with pytest.raises(NotImplementedError):
        x.getPeriod()
    with pytest.raises(NotImplementedError):
        x.setMaxPeriod(0.1)
    with pytest.raises(NotImplementedError):
        x.getStopped()
    with pytest.raises(NotImplementedError):
        x.getDirection()


def test_GenericHID_Hand(wpilib):
    assert hasattr(wpilib.interfaces.GenericHID.Hand, "kLeft")
    assert hasattr(wpilib.interfaces.GenericHID.Hand, "kRight")


def test_GenericHID(wpilib):
    x = wpilib.interfaces.GenericHID(0)
    with pytest.raises(NotImplementedError):
        x.getX()
    with pytest.raises(NotImplementedError):
        x.getY()


def test_NamedSendable(wpilib):
    x = wpilib.interfaces.NamedSendable()
    with pytest.raises(NotImplementedError):
        x.getName()


def test_PIDOutput(wpilib):
    x = wpilib.interfaces.PIDOutput()
    with pytest.raises(NotImplementedError):
        x.pidWrite(0.0)


def test_PIDSource_PIDSourceType(wpilib):
    assert hasattr(wpilib.interfaces.PIDSource.PIDSourceType, "kDisplacement")
    assert hasattr(wpilib.interfaces.PIDSource.PIDSourceType, "kRate")


def test_PIDSource(wpilib):
    x = wpilib.interfaces.PIDSource()
    with pytest.raises(NotImplementedError):
        x.pidGet()


def test_Potentiometer(wpilib):
    x = wpilib.interfaces.Potentiometer()
    with pytest.raises(NotImplementedError):
        x.get()


def test_SpeedController(wpilib):
    x = wpilib.interfaces.SpeedController()
    with pytest.raises(NotImplementedError):
        x.get()
    with pytest.raises(NotImplementedError):
        x.set(0.0)
    with pytest.raises(NotImplementedError):
        x.disable()
