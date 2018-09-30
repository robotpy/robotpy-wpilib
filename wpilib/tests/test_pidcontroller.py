import pytest
import re
from unittest.mock import MagicMock, patch, call


class str_like:
    def __init__(self, regex_str):
        self.regex = re.compile(regex_str)

    def __eq__(self, other):
        return self.regex.fullmatch(other)


@pytest.fixture(scope="function")
def sim_print():
    with patch("wpilib._impl.utils._print", new=MagicMock()) as sim_print:
        yield sim_print


@pytest.fixture(scope="function")
def pid(wpilib, MockNotifier):
    return _get_pid(wpilib)


def _get_pid(wpilib):
    _pid = wpilib.PIDController(
        Kp=1.0, Ki=0.25, Kd=0.75, source=MagicMock(), output=MagicMock()
    )
    _pid.pidInput = MagicMock()
    return _pid


@pytest.fixture(scope="function")
def pid_table(networktables):
    return networktables.NetworkTables.getTable("pidtable")


def test_pidcontroller_init_args1(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, 4.0, source, output, 5.0)

    assert pid.getP() == pytest.approx(1.0, 0.01)
    assert pid.getI() == pytest.approx(2.0, 0.01)
    assert pid.getD() == pytest.approx(3.0, 0.01)
    assert pid.getF() == pytest.approx(4.0, 0.01)
    assert pid.period == pytest.approx(5.0, 0.01)


def test_pidcontroller_init_args2(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, source, output, 5.0)

    assert pid.getP() == pytest.approx(1.0, 0.01)
    assert pid.getI() == pytest.approx(2.0, 0.01)
    assert pid.getD() == pytest.approx(3.0, 0.01)
    assert pid.getF() == pytest.approx(0.0, 0.01)
    assert pid.period == pytest.approx(5.0, 0.01)


def test_pidcontroller_init_args3(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, source, output)

    assert pid.getP() == pytest.approx(1.0, 0.01)
    assert pid.getI() == pytest.approx(2.0, 0.01)
    assert pid.getD() == pytest.approx(3.0, 0.01)
    assert pid.getF() == pytest.approx(0.0, 0.01)
    assert pid.period == pytest.approx(0.05, 0.01)


def test_pidcontroller_init_args4(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, 4.0, source, output)

    assert pid.getP() == pytest.approx(1.0, 0.01)
    assert pid.getI() == pytest.approx(2.0, 0.01)
    assert pid.getD() == pytest.approx(3.0, 0.01)
    assert pid.getF() == pytest.approx(4.0, 0.01)
    assert pid.period == pytest.approx(0.05, 0.01)


def test_pidcontroller_init_args4(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(
        period=5.0, Ki=2.0, Kp=1.0, Kd=3.0, Kf=4.0, source=source, output=output
    )

    assert pid.getP() == pytest.approx(1.0, 0.01)
    assert pid.getI() == pytest.approx(2.0, 0.01)
    assert pid.getD() == pytest.approx(3.0, 0.01)
    assert pid.getF() == pytest.approx(4.0, 0.01)
    assert pid.period == pytest.approx(5.0, 0.01)


def test_pidcontroller_init_args5(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    with pytest.raises(TypeError) as exinfo:
        pid = wpilib.PIDController(Ki=2.0, Kd=3.0, Kf=4.0, source=source, output=output)

    assert (
        exinfo.value.args[0]
        == "__init__() missing 1 required positional argument: 'Kp'"
    )


def test_pidcontroller_init_args6(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    with pytest.raises(TypeError) as exinfo:
        pid = wpilib.PIDController(Kp=2.0, Kd=3.0, Kf=4.0, source=source, output=output)

    assert (
        exinfo.value.args[0]
        == "__init__() missing 1 required positional argument: 'Ki'"
    )


def test_pidcontroller_init_args7(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    with pytest.raises(TypeError) as exinfo:
        pid = wpilib.PIDController(Kp=2.0, Ki=3.0, Kf=4.0, source=source, output=output)

    assert (
        exinfo.value.args[0]
        == "__init__() missing 1 required positional argument: 'Kd'"
    )


def test_pidcontroller_init_args8(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    with pytest.raises(TypeError) as exinfo:
        pid = wpilib.PIDController(Kf=4.0, source=source, output=output)

    assert (
        exinfo.value.args[0]
        == "__init__() missing 3 required positional arguments: 'Kp', 'Ki', and 'Kd'"
    )


def test_pidcontroller_init_args9(wpilib, MockNotifier, sim_print):
    source = lambda: 77.0
    output = MagicMock()
    with pytest.raises(ValueError) as exinfo:
        pid = wpilib.PIDController(Kp=2.0, Ki=3.0, Kd=4.0, output=output)

    assert (
        exinfo.value.args[0]
        == "Attribute error, attributes given did not match any argument templates. See messages above for more info"
    )

    sim_print.assert_has_calls(
        [
            call("**************************************************"),
            call("ERROR: Invalid arguments passed to PIDController.__init__()!!"),
            call("       checking args against 4 possible templates"),
            call("**************************************************"),
            call("Your keyword args: "),
            call(
                str_like(
                    "  output: value [^,]+, type <class 'unittest.mock.MagicMock'>"
                )
            ),
            call("**************************************************"),
            call("Checking template 0: Kf, source, output, period"),
            call("- Error at arg 0: Kf != <class 'float'> or <class 'int'>"),
            call("     your arg: optional; value None <class 'NoneType'>"),
            call(),
            call("Checking template 1: source, output, period"),
            call("- Error at arg 0: source != hasattr(pidGet) or hasattr(__call__)"),
            call("     your arg: optional; value None <class 'NoneType'>"),
            call(),
            call("Checking template 2: source, output"),
            call("- Error at arg 0: source != hasattr(pidGet) or hasattr(__call__)"),
            call("     your arg: optional; value None <class 'NoneType'>"),
            call(),
            call("Checking template 3: Kf, source, output"),
            call("- Error at arg 0: Kf != <class 'float'> or <class 'int'>"),
            call("     your arg: optional; value None <class 'NoneType'>"),
            call(),
            call("**************************************************"),
        ]
    )


def test_pidcontroller_init_args10(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(
        Ki="2.0", Kp=1.0, Kd=3.0, Kf=4.0, source=source, output=output
    )

    assert pid.getP() == pytest.approx(1.0, 0.01)
    # eh?
    assert pid.getI() == "2.0"
    assert pid.getD() == pytest.approx(3.0, 0.01)
    assert pid.getF() == pytest.approx(4.0, 0.01)
    assert pid.period == pytest.approx(0.05, 0.01)


def test_pidcontroller_init_args11(wpilib, MockNotifier, sim_print):
    source = lambda: 77.0
    output = MagicMock()
    with pytest.raises(ValueError) as exinfo:
        pid = wpilib.PIDController(
            Ki=2.0, Kp=1.0, Kd=3.0, Kf="4.0", source=source, output=output
        )

    assert (
        exinfo.value.args[0]
        == "Attribute error, attributes given did not match any argument templates. See messages above for more info"
    )

    sim_print.assert_has_calls(
        [
            call("ERROR: Invalid arguments passed to PIDController.__init__()!!"),
            call("       checking args against 4 possible templates"),
            call("**************************************************"),
            call("Your keyword args: "),
            call("  Kf: value 4.0, type <class 'str'>"),
            call(
                str_like(
                    "  source: value <function test_pidcontroller_init_args11.<locals>.<lambda> at [^>]+>, type <class 'function'>"
                )
            ),
            call(
                str_like("  output: value .+, type <class 'unittest.mock.MagicMock'>")
            ),
            call("**************************************************"),
            call("Checking template 0: Kf, source, output, period"),
            call("- Error at arg 0: Kf != <class 'float'> or <class 'int'>"),
            call("     your arg: keyword; value 4.0 <class 'str'>"),
            call(),
            call("Checking template 1: source, output, period"),
            call("- Error at arg 2: period != <class 'float'> or <class 'int'>"),
            call("     your arg: optional; value None <class 'NoneType'>"),
            call(),
            call("Checking template 2: source, output"),
            call("- Error: unused parameters: Kf"),
            call(),
            call("Checking template 3: Kf, source, output"),
            call("- Error at arg 0: Kf != <class 'float'> or <class 'int'>"),
            call("     your arg: keyword; value 4.0 <class 'str'>"),
            call(),
            call("**************************************************"),
        ],
        any_order=True,
    )


def test_pidcontroller_init_source1(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, source=source, output=output)

    assert pid.pidInput.pidGet() == pytest.approx(77.0, 0.01)
    assert (
        pid.pidInput.getPIDSourceType()
        == wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement
    )


def test_pidcontroller_init_source2(wpilib, MockNotifier):
    class PidInput:
        def pidGet(self):
            return 78.0

        def getPIDSourceType(self):
            return wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kRate

    source = PidInput()
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, source=source, output=output)

    assert pid.pidInput.pidGet() == pytest.approx(78.0, 0.01)
    assert (
        pid.pidInput.getPIDSourceType()
        == wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kRate
    )


def test_pidcontroller_init_output1(wpilib, MockNotifier):
    source = lambda: 77.0
    mock_output = MagicMock()

    def output():
        mock_output()

    pid = wpilib.PIDController(1.0, 2.0, 3.0, source=source, output=output)

    assert pid.pidInput.pidGet() == pytest.approx(77.0, 0.01)
    assert (
        pid.pidInput.getPIDSourceType()
        == wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement
    )

    assert not mock_output.called
    pid.pidOutput()
    assert mock_output.called


def test_pidcontroller_init_output2(wpilib, MockNotifier):
    source = lambda: 77.0
    mock_output = MagicMock()

    class output:
        def pidWrite(self):
            mock_output()

    pid = wpilib.PIDController(1.0, 2.0, 3.0, source=source, output=output())

    assert pid.pidInput.pidGet() == pytest.approx(77.0, 0.01)
    assert (
        pid.pidInput.getPIDSourceType()
        == wpilib.interfaces.pidsource.PIDSource.PIDSourceType.kDisplacement
    )

    assert not mock_output.called
    pid.pidOutput()
    assert mock_output.called


def test_pidcontroller_init_startstask(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, 4.0, source, output, 5.0)

    MockNotifier.assert_called_with(pid._calculate)
    assert pid.controlLoop.startPeriodic.called


def test_pidcontroller_close(pid, MockNotifier):
    pid.removeListeners = MagicMock()
    assert pid.controlLoop.startPeriodic.called
    assert pid.pidInput is not None
    assert pid.pidOutput is not None

    loop = pid.controlLoop
    pid.close()

    assert loop.close.called
    assert pid.controlLoop is None
    assert pid.pidInput is None
    assert pid.pidOutput is None


def test_pidcontroller_calculate_disabled(pid):
    assert not pid.isEnabled()
    pid._calculate()
    assert not pid.pidOutput.called


def test_pidcontroller_calculate_null_source(pid):
    pid.pidInput = None
    pid._calculate()
    assert not pid.pidOutput.called


def test_pidcontroller_calculate_null_output(pid):
    pid.pidOutput = None
    pid._calculate()


def test_pidcontroller_calculate_rate1(pid):
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.pidInput.pidGet.return_value = 45.0
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=1.0, i=0.25, d=0.75, f=0.0)
    pid.enable()

    pid._calculate()

    pid.pidOutput.assert_called_with(1.0)
    assert pid.get() == 1.0


def test_pidcontroller_calculate_rate2(pid):
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.pidInput.pidGet.return_value = 49.50
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=1.0, i=0.25, d=0.75, f=0.0)
    pid.enable()

    pid._calculate()

    assert pid.error == pytest.approx(0.5)
    assert pid.totalError == pytest.approx(0.5)
    pid.pidOutput.assert_called_with(0.875)
    assert pid.get() == 0.875


def test_pidcontroller_calculate_rate3(pid):
    # I does not contribute to calculation for kRate
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.pidInput.pidGet.return_value = 49.50
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=0.0, i=1.00, d=0.00, f=0.0)
    pid.enable()

    pid._calculate()

    pid.pidOutput.assert_called_with(0.0)
    assert pid.get() == 0.0


@pytest.mark.parametrize(
    "source, p, output1, output2",
    [
        (49.5, 1.0, 0.5, 1.0),
        (49.5, 0.5, 0.25, 0.5),
        (49.5, 0.1, 0.05, 0.1),
        (49.9, 1.0, 0.1, 0.2),
        (49.9, 0.5, 0.05, 0.10),
        (49.9, 0.1, 0.01, 0.02),
    ],
)
def test_pidcontroller_calculate_rate4(pid, source, p, output1, output2):
    # P is aggregated error coeff for kRate..
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.pidInput.pidGet.return_value = source
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=p, i=0.0, d=0.00, f=0.0)
    pid.enable()

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output1, 0.01))
    assert pid.get() == pytest.approx(output1, 0.01)
    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output2, 0.01))
    assert pid.get() == pytest.approx(output2, 0.01)


def test_pidcontroller_calculate_rate5(pid):
    # D is proportional error coeff for kRate
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.pidInput.pidGet.return_value = 49.5
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=0.0, i=0.0, d=0.75, f=0.0)
    pid.enable()

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(0.375, 0.01))
    assert pid.get() == pytest.approx(0.375, 0.01)

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(0.375, 0.01))
    assert pid.get() == pytest.approx(0.375, 0.01)

    pid.pidInput.pidGet.return_value = 49.9
    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(0.075, 0.01))
    assert pid.get() == pytest.approx(0.075, 0.01)


def test_pidcontroller_calculate_rate6(pid):
    # F is coeff for some feed forward calc for kRate
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.pidInput.pidGet.return_value = 49.5
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=0.0, i=0.0, d=0.00, f=0.01)
    pid.enable()

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(0.5, 0.01))
    assert pid.get() == pytest.approx(0.5, 0.01)

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(0.5, 0.01))
    assert pid.get() == pytest.approx(0.5, 0.01)

    pid.pidInput.pidGet.return_value = 49.9
    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(0.5, 0.01))
    assert pid.get() == pytest.approx(0.5, 0.01)


@pytest.mark.parametrize(
    "continuous, input, setpoint, expected_error, expected_output",
    [
        (False, 180.5, 179.9, -0.6, -0.105),
        (False, 360.5, 179.9, -180.6, -1.0),
        (False, 0.5, 179.9, 179.4, 1.0),
        (True, 180.5, 179.9, -0.6, -0.105),
        (True, 360.5, 179.9, 179.4, 1.0),
        (True, 0.5, 179.9, 179.4, 1.0),
    ],
)
def test_pidcontroller_calculate_rate7(
    pid, continuous, input, setpoint, expected_error, expected_output
):
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.pidInput.pidGet.return_value = input
    pid.setInputRange(-180.0, 180.0)
    pid.setContinuous(continuous)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(setpoint)
    pid.setPID(p=0.1, i=0.0, d=0.075, f=0.0)
    pid.enable()

    pid._calculate()

    assert pid.error == pytest.approx(expected_error, 0.01)
    pid.pidOutput.assert_called_with(pytest.approx(expected_output, 0.01))
    assert pid.get() == pytest.approx(expected_output, 0.01)


@pytest.mark.parametrize(
    "p, source1, source2, output1, output2",
    [(1.0, 49.5, 49.9, 0.5, 0.1), (0.5, 49.5, 49.9, 0.25, 0.05)],
)
def test_pidcontroller_calculate_displacement1(
    pid, p, source1, source2, output1, output2
):
    # P is proportional error coeff for kDisplacement
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kDisplacement
    pid.pidInput.pidGet.return_value = source1
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=p, i=0.0, d=0.00, f=0.0)
    pid.enable()

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output1, 0.01))
    assert pid.get() == pytest.approx(output1, 0.01)

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output1, 0.01))
    assert pid.get() == pytest.approx(output1, 0.01)

    pid.pidInput.pidGet.return_value = source2
    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output2, 0.01))
    assert pid.get() == pytest.approx(output2, 0.01)


@pytest.mark.parametrize(
    "i, source1, source2, output1, output2, output3",
    [
        (1.0, 49.5, 49.9, 0.5, 1.0, 1.0),
        (0.5, 49.5, 49.9, 0.25, 0.5, 0.55),
        (1.0, 49.5, 50.6, 0.5, 1.0, 0.4),
    ],
)
def test_pidcontroller_calculate_displacement2(
    pid, i, source1, source2, output1, output2, output3
):
    # I is aggregated error coeff for kDisplacement
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kDisplacement
    pid.pidInput.pidGet.return_value = source1
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=0, i=i, d=0.00, f=0.0)
    pid.enable()

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output1, 0.01))
    assert pid.get() == pytest.approx(output1, 0.01)

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output2, 0.01))
    assert pid.get() == pytest.approx(output2, 0.01)

    pid.pidInput.pidGet.return_value = source2
    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output3, 0.01))
    assert pid.get() == pytest.approx(output3, 0.01)


@pytest.mark.parametrize(
    "d, source1, source2, output1, output2, output3",
    [
        (1.0, 49.5, 49.9, 0.5, 0.0, -0.4),
        (0.5, 49.5, 49.9, 0.25, 0.0, -0.2),
        (1.0, 49.5, 50.6, 0.5, 0.0, -1.0),
    ],
)
def test_pidcontroller_calculate_displacement3(
    pid, d, source1, source2, output1, output2, output3
):
    # D is change in error coeff for kDisplacement
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kDisplacement
    pid.pidInput.pidGet.return_value = source1
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=0, i=0, d=d, f=0.0)
    pid.enable()

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output1, 0.01))
    assert pid.get() == pytest.approx(output1, 0.01)

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output2, 0.01))
    assert pid.get() == pytest.approx(output2, 0.01)

    pid.pidInput.pidGet.return_value = source2
    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output3, 0.01))
    assert pid.get() == pytest.approx(output3, 0.01)


@pytest.mark.parametrize(
    "f, source1, source2, output1, output2, output3",
    [
        (1.0, 49.5, 49.9, 1.0, 0.0, 0.0),
        (0.5, 49.5, 49.9, 1.0, 0.0, 0.0),
        (1.0, 49.5, 50.6, 1.0, 0.0, 0.0),
    ],
)
def test_pidcontroller_calculate_displacement4(
    pid, f, source1, source2, output1, output2, output3
):
    # F is coeff for some feed forward calc for kDisplacement
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kDisplacement
    pid.pidInput.pidGet.return_value = source1
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(50.0)
    pid.setPID(p=0, i=0, d=0, f=f)
    pid.enable()

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output1, 0.01))
    assert pid.get() == pytest.approx(output1, 0.01)

    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output2, 0.01))
    assert pid.get() == pytest.approx(output2, 0.01)

    pid.pidInput.pidGet.return_value = source2
    pid._calculate()
    pid.pidOutput.assert_called_with(pytest.approx(output3, 0.01))
    assert pid.get() == pytest.approx(output3, 0.01)


@pytest.mark.parametrize(
    "f, setpoint, expected", [(1.0, 50.0, 50.0), (0.5, 50.0, 25.0)]
)
def test_pidcontroller_calculateFeedForward_rate(pid, f, setpoint, expected):
    pid.pidInput.getPIDSourceType.return_value = pid.PIDSourceType.kRate
    pid.setInputRange(0, 100.0)
    pid.setOutputRange(-1, 1)
    pid.setSetpoint(setpoint)
    pid.setPID(p=0, i=0, d=0, f=f)

    assert pid.calculateFeedForward() == pytest.approx(expected, 0.01)


def test_pidcontroller_calculateFeedForward_displacement(
    sim_hooks, wpilib, MockNotifier
):
    sim_hooks.time = 1.0
    pid0 = _get_pid(wpilib)
    assert pid0.setpointTimer.get() == pytest.approx(0.0, 0.01)
    sim_hooks.time = 2.0
    assert pid0.setpointTimer.get() == pytest.approx(1.0, 0.01)
    pid0.pidInput.getPIDSourceType.return_value = pid0.PIDSourceType.kDisplacement
    pid0.setInputRange(0, 100.0)
    pid0.setOutputRange(-1, 1)
    pid0.setSetpoint(50.0)
    pid0.setPID(p=0, i=0, d=0, f=1.0)

    assert pid0.calculateFeedForward() == pytest.approx(50.0, 0.01)
    sim_hooks.time = 4.0
    pid0.setSetpoint(55.0)
    assert pid0.setpointTimer.get() == pytest.approx(2.0, 0.01)
    assert pid0.calculateFeedForward() == pytest.approx(2.5, 0.01)
    assert pid0.setpointTimer.get() == pytest.approx(0.0, 0.01)
    sim_hooks.time = 8.0
    pid0.setSetpoint(60.0)
    assert pid0.setpointTimer.get() == pytest.approx(4.0, 0.01)
    assert pid0.calculateFeedForward() == pytest.approx(1.25, 0.01)
    assert pid0.setpointTimer.get() == pytest.approx(0.0, 0.01)


@pytest.mark.parametrize("p,i,d,f", [(1.0, 2.0, 3.0, 4.0)])
def test_pidcontroller_setPID(pid, p, i, d, f):
    pid.setPID(p, i, d, f)
    assert pid.getP() == p
    assert pid.getI() == i
    assert pid.getD() == d
    assert pid.getF() == f


@pytest.mark.parametrize(
    "setpoint, lower, upper, new_setpoint",
    [
        (1.5, 1.0, 2.0, 1.5),
        (3.0, 1.0, 2.0, 2.0),
        (0.0, 1.0, 2.0, 1.0),
        (2.0, 1.0, 1.0, 2.0),
    ],
)
def test_pidcontroller_setInputRange1(pid, setpoint, lower, upper, new_setpoint):
    pid.setSetpoint(setpoint)
    pid.setInputRange(lower, upper)

    assert pid.minimumInput == lower
    assert pid.maximumInput == upper
    assert pid.getSetpoint() == new_setpoint


def test_pidcontroller_setInputRange2(pid, pid_table):
    with pytest.raises(ValueError) as exinfo:
        pid.setInputRange(2.0, 1.0)

    assert exinfo.value.args[0] == "Lower bound is greater than upper bound"


def test_pidcontroller_setOutputRange1(pid):
    pid.setOutputRange(1.0, 2.0)

    assert pid.minimumOutput == 1.0
    assert pid.maximumOutput == 2.0


def test_pidcontroller_setOutputRange2(pid, pid_table):
    with pytest.raises(ValueError) as exinfo:
        pid.setOutputRange(2.0, 1.0)

    assert exinfo.value.args[0] == "Lower bound is greater than upper bound"


def test_pidcontroller_setSetpoint1(pid):
    pid.setSetpoint(1.0)

    assert pid.getSetpoint() == 1.0


def test_pidcontroller_setSetpoint2(pid, sendablebuilder):
    pid.initSendable(sendablebuilder)
    assert sendablebuilder.getTable().getNumber("setpoint", 0.0) == 0.0
    pid.setSetpoint(1.0)
    sendablebuilder.updateTable()
    assert sendablebuilder.getTable().getNumber("setpoint", 0.0) == 1.0


def test_pidcontroller_setPIDSourceType1(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, 4.0, source, output, 5.0)

    with pytest.raises(NotImplementedError):
        pid.setPIDSourceType(pid.PIDSourceType.kRate)


def test_pidcontroller_setPIDSourceType2(wpilib, MockNotifier):
    source = MagicMock()
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, 4.0, source, output, 5.0)

    pid.setPIDSourceType(pid.PIDSourceType.kRate)

    assert source.setPIDSourceType.called_with(pid.PIDSourceType.kRate)


def test_pidcontroller_getPIDSourceType1(wpilib, MockNotifier):
    source = lambda: 77.0
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, 4.0, source, output, 5.0)

    assert pid.getPIDSourceType() == pid.PIDSourceType.kDisplacement


def test_pidcontroller_getPIDSourceType2(wpilib, MockNotifier):
    source = MagicMock()
    output = MagicMock()
    pid = wpilib.PIDController(1.0, 2.0, 3.0, 4.0, source, output, 5.0)

    pid.getPIDSourceType()

    assert source.getPIDSourceType.called


@pytest.mark.parametrize("p,i,d,f,setpoint,enabled", [(1.0, 2.0, 3.0, 4.0, 5.0, True)])
def test_pidcontroller_initSendable_update(
    pid, sendablebuilder, p, i, d, f, setpoint, enabled
):
    pid.initSendable(sendablebuilder)
    assert sendablebuilder.getTable().getNumber("p", 0.0) == 0.0
    assert sendablebuilder.getTable().getNumber("i", 0.0) == 0.0
    assert sendablebuilder.getTable().getNumber("d", 0.0) == 0.0
    assert sendablebuilder.getTable().getNumber("f", 0.0) == 0.0
    assert sendablebuilder.getTable().getNumber("setpoint", 0.0) == 0.0
    assert sendablebuilder.getTable().getBoolean("enabled", None) is None
    pid.setSetpoint(setpoint)
    pid.setEnabled(enabled)
    pid.setPID(p, i, d, f)
    sendablebuilder.updateTable()
    assert sendablebuilder.getTable().getNumber("p", 0.0) == pytest.approx(p, 0.01)
    assert sendablebuilder.getTable().getNumber("i", 0.0) == pytest.approx(i, 0.01)
    assert sendablebuilder.getTable().getNumber("d", 0.0) == pytest.approx(d, 0.01)
    assert sendablebuilder.getTable().getNumber("f", 0.0) == pytest.approx(f, 0.01)
    assert sendablebuilder.getTable().getNumber("setpoint", 0.0) == pytest.approx(
        setpoint, 0.01
    )
    assert sendablebuilder.getTable().getBoolean("enabled", None) == enabled


@pytest.mark.parametrize("p,i,d,f,setpoint,enabled", [(1.0, 2.0, 3.0, 4.0, 5.0, True)])
def test_pidcontroller_initSendable_setter(
    pid, sendablebuilder, p, i, d, f, setpoint, enabled
):
    pid.initSendable(sendablebuilder)
    [
        p_prop,
        i_prop,
        d_prop,
        f_prop,
        setpoint_prop,
        enabled_prop,
    ] = sendablebuilder.properties
    assert p_prop.key == "p"
    assert i_prop.key == "i"
    assert d_prop.key == "d"
    assert f_prop.key == "f"
    assert setpoint_prop.key == "setpoint"
    assert enabled_prop.key == "enabled"

    p_prop.setter(p)
    assert pid.getP() == p

    i_prop.setter(i)
    assert pid.getI() == i

    d_prop.setter(d)
    assert pid.getD() == d

    f_prop.setter(f)
    assert pid.getF() == f

    setpoint_prop.setter(setpoint)
    assert pid.getSetpoint() == setpoint

    enabled_prop.setter(enabled)
    assert pid.isEnabled() == enabled


def test_pidcontroller_initSendable_safe(pid, sendablebuilder):
    pid.reset = MagicMock()
    pid.initSendable(sendablebuilder)
    sendablebuilder.startLiveWindowMode()
    assert pid.reset.called


@pytest.mark.parametrize(
    "error, input_range, expected, continuous",
    [
        # fmt: off
        # the % operator has different semantics in java and python,
        # so it is possible the behavior of getContinuousError can/will differ.
        # be sure expected values are obtained/validated from the java 
        # implementation
        ( 1.80, 2.00, -0.20, True),
        (-1.80, 2.00,  0.20, True),
        ( 0.80, 2.00,  0.80, True),
        (-0.80, 2.00, -0.80, True),
        ( 1.80, 2.00,  1.80, False),
        (-1.80, 2.00, -1.80, False),
        ( 0.80, 2.00,  0.80, False),
        (-0.80, 2.00, -0.80, False),
        # fmt: on
    ],
)
def test_pidcontroller_getContinuousError(
    pid, error, input_range, expected, continuous
):
    pid.setInputRange(0, input_range)
    pid.setContinuous(continuous)
    result = pid.getContinuousError(error)
    assert pid.inputRange == input_range
    assert pid.continuous == continuous
    assert result == pytest.approx(expected, 0.01)


def test_pidcontroller_reset(pid):
    pid.setEnabled(True)
    pid.reset()
    assert not pid.isEnabled()
