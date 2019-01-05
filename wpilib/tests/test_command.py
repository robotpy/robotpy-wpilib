import pytest
from unittest.mock import MagicMock, call, patch


@pytest.fixture(scope="function")
def command(wpilib):
    return wpilib.command.Command()


def test_command_init1(wpilib):
    command = wpilib.command.Command()
    assert command.getName() == "Command"
    assert command.timeout == -1
    assert len(command.requirements) == 0


def test_command_init2(wpilib):
    command = wpilib.command.Command("Percival")
    assert command.getName() == "Percival"
    assert command.timeout == -1
    assert len(command.requirements) == 0


def test_command_init3(wpilib):
    command = wpilib.command.Command(timeout=2.0)
    assert command.getName() == "Command"
    assert command.timeout == 2.0
    assert len(command.requirements) == 0


def test_command_init4(wpilib):
    command = wpilib.command.Command(name="Percival", timeout=2.0)
    assert command.getName() == "Percival"
    assert command.timeout == 2.0
    assert len(command.requirements) == 0


def test_command_init5(wpilib):
    subsystem = wpilib.command.Subsystem()
    command = wpilib.command.Command(name="Percival", timeout=2.0, subsystem=subsystem)

    assert command.getName() == "Percival"
    assert command.timeout == 2.0
    assert subsystem in command.requirements


def test_command_setTimeout(command):
    command.setTimeout(2.0)
    assert command.timeout == 2.0


def test_command_timeSinceInitialized(wpilib, sim_hooks):
    sim_hooks.time = 0.0
    command = wpilib.command.Command()
    assert command.timeSinceInitialized() == 0.0
    sim_hooks.time = 2.0

    command.startTiming()
    sim_hooks.time = 5.0
    assert command.timeSinceInitialized() == pytest.approx(3.0)


def test_command_isTimedOut1(wpilib, sim_hooks):
    command = wpilib.command.Command()
    sim_hooks.time = 0.0

    command.startTiming()
    sim_hooks.time = 5.0
    assert not command.isTimedOut()
    sim_hooks.time = 500000.0
    assert not command.isTimedOut()


def test_command_isTimedOut2(wpilib, sim_hooks):
    command = wpilib.command.Command(timeout=2.0)
    sim_hooks.time = 0.0

    command.startTiming()
    sim_hooks.time = 1.9
    assert not command.isTimedOut()
    sim_hooks.time = 2.1
    assert command.isTimedOut()


def test_command_requires1(command, wpilib):
    subsystem = wpilib.command.Subsystem()

    command.requires(subsystem)

    assert subsystem in command.requirements


def test_command_requires2(command, wpilib):
    subsystem = wpilib.command.Subsystem()

    command.lockChanges()

    with pytest.raises(ValueError) as excinfo:
        command.requires(subsystem)

    assert excinfo.value.args[0] == "Can not add new requirement to command"


def test_command_requires3(command):
    with pytest.raises(ValueError) as excinfo:
        command.requires(None)

    assert excinfo.value.args[0] == "Subsystem must not be None."


def test_command_removed1(command):
    mock = MagicMock()
    command.end = lambda: mock("end")
    command.interrupted = lambda: mock("interrupted")

    command.removed()

    mock.assert_has_calls([])


def test_command_removed2(command, enable_robot):
    mock = MagicMock()
    command.end = lambda: mock("end")
    command.interrupted = lambda: mock("interrupted")

    command.startRunning()
    command.run()

    command.removed()

    mock.assert_has_calls([call("end")])


def test_command_removed3(command, enable_robot):
    mock = MagicMock()
    command.end = lambda: mock("end")
    command.interrupted = lambda: mock("interrupted")

    command.startRunning()
    command.run()

    command.removed()
    command.removed()

    mock.assert_has_calls([call("end")])


def test_command_removed4(command, enable_robot):
    mock = MagicMock()
    command.end = lambda: mock("end")
    command.interrupted = lambda: mock("interrupted")

    command.startRunning()
    command.run()
    command.cancel()

    command.removed()

    mock.assert_has_calls([call("interrupted")])


def test_command_removed5(command, enable_robot):
    mock = MagicMock()
    command.end = lambda: mock("end")
    command.interrupted = lambda: mock("interrupted")

    command.startRunning()
    command.run()
    command.cancel()

    command.removed()
    command.removed()

    mock.assert_has_calls([call("interrupted")])


def test_command_run1(command, enable_robot):
    mock = MagicMock()
    command.initialize = lambda: mock("initialize")
    command.execute = lambda: mock("execute")

    command.startRunning()
    command.run()

    mock.assert_has_calls([call("initialize"), call("execute")])


def test_command_run2(command, enable_robot):
    mock = MagicMock()
    command.initialize = lambda: mock("initialize")
    command.execute = lambda: mock("execute")

    command.startRunning()
    command.run()
    command.run()
    command.run()

    mock.assert_has_calls(
        [call("initialize"), call("execute"), call("execute"), call("execute")]
    )


def test_command_run3(command):
    mock = MagicMock()
    command.initialize = lambda: mock("initialize")
    command.execute = lambda: mock("execute")

    command.startRunning()
    command.cancel()
    command.run()

    mock.assert_has_calls([])


@pytest.mark.parametrize(
    "is_finished, is_canceled, expected",
    [
        (True, False, False),
        (False, False, True),
        (True, True, False),
        (False, True, False),
    ],
)
def test_command_run4(command, is_finished, is_canceled, expected):
    command.isFinished = MagicMock(return_value=is_finished)
    command.isCanceled = MagicMock(return_value=is_canceled)
    assert command.run() == expected


def test_command_run5(command, disable_robot):
    command.cancel = MagicMock()
    command.run()

    assert command.cancel.called


def test_command_run6(command, disable_robot):
    command.cancel = MagicMock()
    command.setRunWhenDisabled(True)
    command.run()

    assert not command.cancel.called


def test_command_getRequirements(command, wpilib):
    subsystem = wpilib.command.Subsystem()
    command.requires(subsystem)
    assert subsystem in command.requirements

    reqs = command.getRequirements()
    reqs.remove(subsystem)
    assert subsystem not in reqs
    assert subsystem in command.requirements


def test_command_setParent(command, wpilib):
    parent = wpilib.command.CommandGroup()

    assert not command.isParented()
    command.setParent(parent)
    assert command.isParented()


def test_command_clearRequirements(command, wpilib):
    subsystem = wpilib.command.Subsystem()
    command.requires(subsystem)
    assert subsystem in command.requirements

    command.clearRequirements()
    assert subsystem not in command.requirements


def test_command_initSendable_update(command, sendablebuilder):
    command.initSendable(sendablebuilder)
    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getString(".name", "") == "Command"
    assert sendablebuilder.getTable().getBoolean("running", None) == False
    assert sendablebuilder.getTable().getBoolean(".isParented", None) == False


def test_command_initSendable_set1(command, sendablebuilder):
    command.initSendable(sendablebuilder)

    assert sendablebuilder.properties[0].key == ".name"
    assert sendablebuilder.properties[1].key == "running"
    assert sendablebuilder.properties[2].key == ".isParented"


@pytest.mark.parametrize(
    "input, is_running, start_called, cancel_called",
    [
        (True, True, False, False),
        (True, False, True, False),
        (False, True, False, True),
        (False, False, False, False),
    ],
)
def test_command_initSendable_set2(
    command, sendablebuilder, input, is_running, start_called, cancel_called
):
    command.initSendable(sendablebuilder)
    command.start = MagicMock()
    command.cancel = MagicMock()
    command.isRunning = MagicMock(return_value=is_running)

    prop = sendablebuilder.properties[1]
    assert prop.key == "running"
    assert prop.setter is not None

    prop.setter(input)
    assert command.cancel.called == cancel_called
    assert command.start.called == start_called


def test_instantcommand_init1(wpilib):
    command = wpilib.command.InstantCommand()

    assert command.getName() == "InstantCommand"
    assert command.timeout == -1
    assert len(command.requirements) == 0


def test_instantcommand_init2(wpilib):
    command = wpilib.command.InstantCommand("Percival")

    assert command.getName() == "Percival"
    assert command.timeout == -1
    assert len(command.requirements) == 0


def test_instantcommand_init3(wpilib):
    subsystem = wpilib.command.Subsystem()
    command = wpilib.command.InstantCommand("Percival", subsystem)

    assert command.getName() == "Percival"
    assert command.timeout == -1
    assert subsystem in command.requirements


def test_timedcommand_init1(wpilib):
    command = wpilib.command.TimedCommand("Percival", 3.0)

    assert command.getName() == "Percival"
    assert command.timeout == 3.0
    assert len(command.requirements) == 0


def test_timedcommand_init2(wpilib):
    subsystem = wpilib.command.Subsystem()
    command = wpilib.command.TimedCommand("Percival", 3.0, subsystem)

    assert command.getName() == "Percival"
    assert command.timeout == 3.0
    assert subsystem in command.requirements


def test_pidcommand_init1(wpilib, MockNotifier):
    command = wpilib.command.PIDCommand(1.0, 2.0, 3.0)

    assert command.getName() == "PIDCommand"
    assert command.timeout == -1
    assert command.controller is not None
    assert command.controller.getP() == pytest.approx(1.0, 0.01)
    assert command.controller.getI() == pytest.approx(2.0, 0.01)
    assert command.controller.getD() == pytest.approx(3.0, 0.01)
    assert command.controller.period == wpilib.PIDController.kDefaultPeriod
    assert command.controller.getF() == pytest.approx(0, 0.01)
    assert len(command.requirements) == 0


def test_pidcommand_init2(wpilib, MockNotifier):
    command = wpilib.command.PIDCommand(1.0, 2.0, 3.0, 4.0)

    assert command.getName() == "PIDCommand"
    assert command.timeout == -1
    assert command.controller is not None
    assert command.controller.getP() == pytest.approx(1.0, 0.01)
    assert command.controller.getI() == pytest.approx(2.0, 0.01)
    assert command.controller.getD() == pytest.approx(3.0, 0.01)
    assert command.controller.period == pytest.approx(4.0, 0.01)
    assert command.controller.getF() == pytest.approx(0, 0.01)
    assert len(command.requirements) == 0


def test_pidcommand_init3(wpilib, MockNotifier):
    command = wpilib.command.PIDCommand(1.0, 2.0, 3.0, 4.0, 5.0)

    assert command.getName() == "PIDCommand"
    assert command.timeout == -1
    assert command.controller is not None
    assert command.controller.getP() == pytest.approx(1.0, 0.01)
    assert command.controller.getI() == pytest.approx(2.0, 0.01)
    assert command.controller.getD() == pytest.approx(3.0, 0.01)
    assert command.controller.period == pytest.approx(4.0, 0.01)
    assert command.controller.getF() == pytest.approx(5.0, 0.01)
    assert len(command.requirements) == 0


def test_pidcommand_init4(wpilib, MockNotifier):
    command = wpilib.command.PIDCommand(1.0, 2.0, 3.0, 4.0, 5.0, "Percival")

    assert command.getName() == "Percival"
    assert command.timeout == -1
    assert command.controller is not None
    assert command.controller.getP() == pytest.approx(1.0, 0.01)
    assert command.controller.getI() == pytest.approx(2.0, 0.01)
    assert command.controller.getD() == pytest.approx(3.0, 0.01)
    assert command.controller.period == pytest.approx(4.0, 0.01)
    assert command.controller.getF() == pytest.approx(5.0, 0.01)
    assert len(command.requirements) == 0


def test_pidcommand_init5(wpilib, MockNotifier):
    subsystem = wpilib.command.Subsystem()
    command = wpilib.command.PIDCommand(1.0, 2.0, 3.0, 4.0, 5.0, "Percival", subsystem)

    assert command.getName() == "Percival"
    assert command.timeout == -1
    assert command.controller is not None
    assert command.controller.getP() == pytest.approx(1.0, 0.01)
    assert command.controller.getI() == pytest.approx(2.0, 0.01)
    assert command.controller.getD() == pytest.approx(3.0, 0.01)
    assert command.controller.period == pytest.approx(4.0, 0.01)
    assert command.controller.getF() == pytest.approx(5.0, 0.01)
    assert subsystem in command.requirements
