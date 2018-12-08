import pytest
from unittest.mock import MagicMock, call, patch


@pytest.fixture(scope="function")
def scheduler(wpilib):
    return wpilib.command.Scheduler()


def test_scheduler_add(scheduler):
    command = MagicMock()
    scheduler.add(command)

    assert command in scheduler.additions
    assert command not in scheduler.commandTable

    scheduler.run()

    assert not command.run.called
    assert command not in scheduler.additions
    assert command in scheduler.commandTable


def test_scheduler__add1(scheduler):
    # doesn't add same command twice
    command = MagicMock()
    scheduler._add(command)

    assert len(scheduler.commandTable) == 1
    assert scheduler.runningCommandsChanged == True
    scheduler.runningCommandsChanged = False

    scheduler._add(command)

    assert len(scheduler.commandTable) == 1
    assert scheduler.runningCommandsChanged == False


def test_scheduler__add2(scheduler, wpilib):
    # doesn't add if another command is hogging requirement
    command1 = MagicMock()
    command2 = MagicMock()
    command2.isInterruptible.return_value = False
    requirement = wpilib.command.Subsystem()
    requirement.setCurrentCommand(command2)
    command1.getRequirements.return_value = [requirement]
    scheduler._add(command2)

    assert command2 in scheduler.commandTable

    scheduler._add(command1)
    assert command1 not in scheduler.commandTable


def test_scheduler__add2(scheduler, wpilib):
    # replace if another command is using requirement
    command1 = MagicMock()
    command2 = MagicMock()
    command2.isInterruptible.return_value = True
    requirement = wpilib.command.Subsystem()
    requirement.setCurrentCommand(command2)
    command1.getRequirements.return_value = [requirement]
    scheduler._add(command2)

    assert command2 in scheduler.commandTable

    scheduler._add(command1)
    assert command1 in scheduler.commandTable
    assert command2 not in scheduler.commandTable
    assert command2.cancel.called


def test_scheduler_run1(scheduler):
    # calls buttons, last in called first
    mock = MagicMock()

    scheduler.addButton(lambda: mock(1))
    scheduler.addButton(lambda: mock(2))
    scheduler.run()

    mock.assert_has_calls([call(2), call(1)], any_order=False)


def test_scheduler_run2(scheduler, wpilib):
    # calls subsystems, no order
    mock = MagicMock()

    subsystem1 = wpilib.command.Subsystem()
    subsystem1.periodic = lambda: mock(1)
    subsystem2 = wpilib.command.Subsystem()
    subsystem2.periodic = lambda: mock(2)
    scheduler.registerSubsystem(subsystem1)
    scheduler.registerSubsystem(subsystem2)
    scheduler.run()

    mock.assert_has_calls([call(1), call(2)], any_order=True)


def test_scheduler_run3(scheduler, wpilib):
    # calls commands, first in called first
    mock = MagicMock()

    def callmock(i):
        mock(i)
        return True

    command1 = wpilib.command.Command()
    command1.run = lambda: callmock(1)
    command2 = wpilib.command.Command()
    command2.run = lambda: callmock(2)
    command3 = wpilib.command.Command()
    command3.run = lambda: callmock(3)
    scheduler._add(command1)
    scheduler._add(command2)
    scheduler._add(command3)
    scheduler.run()

    mock.assert_has_calls([call(1), call(2), call(3)], any_order=False)
    assert not scheduler.runningCommandsChanged


def test_scheduler_run4(scheduler, wpilib):
    # removes done commands
    command1 = wpilib.command.Command()
    command1.run = lambda: True
    command2 = wpilib.command.Command()
    command2.run = lambda: False
    scheduler._add(command1)
    scheduler._add(command2)
    scheduler.run()

    assert command1 in scheduler.commandTable
    assert command2 not in scheduler.commandTable
    assert scheduler.runningCommandsChanged


def test_scheduler_run4(scheduler, wpilib):
    # adds subsystem's default command
    command1 = wpilib.command.Command()
    requirement = wpilib.command.Subsystem()
    command1.requires(requirement)
    requirement.setDefaultCommand(command1)
    scheduler.registerSubsystem(requirement)
    scheduler.run()

    assert command1 in scheduler.commandTable


def test_scheduler_remove(scheduler, wpilib):
    # removes command from schedule and from requirement
    command1 = wpilib.command.Command()
    command1.removed = MagicMock()
    requirement = wpilib.command.Subsystem()
    command1.requires(requirement)
    requirement.setCurrentCommand(command1)
    scheduler.registerSubsystem(requirement)
    scheduler._add(command1)

    assert command1 in scheduler.commandTable
    assert requirement.getCurrentCommand() == command1

    scheduler.remove(command1)
    assert command1 not in scheduler.commandTable
    assert requirement.getCurrentCommand() is None
    assert command1.removed.called


def test_scheduler_removeAll(scheduler, wpilib):
    # removes command from schedule and from requirement
    command1 = wpilib.command.Command()
    command1.removed = MagicMock()
    requirement = wpilib.command.Subsystem()
    command1.requires(requirement)
    requirement.setCurrentCommand(command1)
    scheduler.registerSubsystem(requirement)
    scheduler._add(command1)

    assert command1 in scheduler.commandTable
    assert requirement.getCurrentCommand() == command1

    scheduler.removeAll()
    assert command1 not in scheduler.commandTable
    assert requirement.getCurrentCommand() is None
    assert command1.removed.called


def test_scheduler_disable(scheduler, wpilib):
    # adds subsystem's default command
    mock = MagicMock()

    scheduler.addButton(lambda: mock(1))
    scheduler.addButton(lambda: mock(2))
    scheduler.disable()
    scheduler.run()

    assert not mock.called

    scheduler.enable()
    scheduler.run()

    assert mock.called


def test_scheduler_initSendable(scheduler, sendablebuilder):
    scheduler._updateTable = MagicMock()
    scheduler.initSendable(sendablebuilder)

    assert sendablebuilder.getTable().getString(".type", "") == "Scheduler"

    sendablebuilder.updateTable()

    assert sendablebuilder._updateTable == scheduler._updateTable
    assert scheduler._updateTable.called


def test_scheduler_updateTable1(scheduler, wpilib, sendablebuilder):
    # publishes command ids and names
    command = wpilib.command.Command()
    scheduler._add(command)
    scheduler.initSendable(sendablebuilder)

    sendablebuilder.updateTable()
    assert sendablebuilder.getTable().getEntry("Ids").getDoubleArray([]) == (
        float(id(command)),
    )
    assert sendablebuilder.getTable().getEntry("Names").getStringArray([]) == (
        "Command",
    )


@pytest.mark.parametrize("_id", [11, -9223363293403863878, None])
def test_scheduler_updateTable2(scheduler, wpilib, sendablebuilder, _id):
    # cancels command
    command = wpilib.command.Command()
    command.cancel = MagicMock()
    if _id is None:
        fake_id = id
        _id = id(command)
    else:
        fake_id = lambda x: _id
    scheduler._add(command)
    scheduler.initSendable(sendablebuilder)

    sendablebuilder.getTable().getEntry("Cancel").setDoubleArray([float(_id)])
    with patch("builtins.id", new=fake_id):
        sendablebuilder.updateTable()

    assert command.cancel.called, "failed with hash=%s" % (command.__hash__(),)
    assert command in scheduler.commandTable
