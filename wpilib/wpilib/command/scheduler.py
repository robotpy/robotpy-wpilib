# validated: 2018-10-30 EN e2100730447d edu/wpi/first/wpilibj/command/Scheduler.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from ..sendablebase import SendableBase

import collections
import warnings

__all__ = ["Scheduler"]


class Scheduler(SendableBase):
    """The Scheduler is a singleton which holds the top-level running commands.
    It is in charge of both calling the command's run() method and to make
    sure that there are no two commands with conflicting requirements running.

    It is fine if teams wish to take control of the Scheduler themselves, all
    that needs to be done is to call Scheduler.getInstance().run() often to
    have Commands function correctly. However, this is already done for you
    if you use the CommandBased Robot template.

    .. seealso:: :class:`.Command`
    """

    @staticmethod
    def _reset():
        try:
            del Scheduler.instance
        except:
            pass

    @staticmethod
    def getInstance():
        """Returns the Scheduler, creating it if one does not exist.

        :returns: the Scheduler
        """
        if not hasattr(Scheduler, "instance"):
            Scheduler.instance = Scheduler()
        return Scheduler.instance

    def __init__(self):
        """Instantiates a Scheduler.
        """
        super().__init__()
        hal.report(
            hal.UsageReporting.kResourceType_Command,
            hal.UsageReporting.kCommand_Scheduler,
        )
        self.setName("Scheduler")

        # Active Commands
        self.commandTable = collections.OrderedDict()
        # The set of all Subsystems
        self.subsystems = set()
        # Whether or not we are currently adding a command
        self.adding = False
        # Whether or not we are currently disabled
        self.disabled = False
        # A list of all Commands which need to be added
        self.additions = []
        # A list of all Buttons. It is created lazily.
        self.buttons = []
        self.runningCommandsChanged = False

        self.namesEntry = None
        self.idsEntry = None
        self.cancelEntry = None

    def add(self, command):
        """Adds the command to the Scheduler. This will not add the
        :class:`.Command` immediately, but will instead wait for the proper time in
        the :meth:`run` loop before doing so. The command returns immediately
        and does nothing if given null.

        Adding a :class:`.Command` to the :class:`.Scheduler` involves the
        Scheduler removing any Command which has shared requirements.

        :param command: the command to add
        """
        if command is not None:
            self.additions.append(command)

    def addButton(self, button):
        """Adds a button to the Scheduler. The Scheduler will poll
        the button during its :meth:`run`.

        :param button: the button to add
        """
        self.buttons.append(button)

    def _add(self, command):
        """Adds a command immediately to the Scheduler. This should only be
        called in the :meth:`run` loop. Any command with conflicting
        requirements will be removed, unless it is uninterruptable. Giving
        None does nothing.

        :param command: the :class:`.Command` to add
        """
        if command is None:
            return

        # Check to make sure no adding during adding
        if self.adding:
            warnings.warn(
                "Can not start command from cancel method.  Ignoring: %s" % command,
                RuntimeWarning,
            )
            return

        # Only add if not already in
        if command not in self.commandTable:
            # Check that the requirements can be had
            for lock in command.getRequirements():
                if (
                    lock.getCurrentCommand() is not None
                    and not lock.getCurrentCommand().isInterruptible()
                ):
                    return

            # Give it the requirements
            self.adding = True
            for lock in command.getRequirements():
                if lock.getCurrentCommand() is not None:
                    lock.getCurrentCommand().cancel()
                    self.remove(lock.getCurrentCommand())
                lock.setCurrentCommand(command)
            self.adding = False

            # Add it to the list
            self.commandTable[command] = 1

            self.runningCommandsChanged = True

            command.startRunning()

    def run(self):
        """Runs a single iteration of the loop. This method should be called
        often in order to have a functioning Command system. The loop has five
        stages:

        - Poll the Buttons
        - Execute/Remove the Commands
        - Send values to SmartDashboard
        - Add Commands
        - Add Defaults
        """

        self.runningCommandsChanged = False

        if self.disabled:
            return  # Don't run when disabled

        # Get button input (going backwards preserves button priority)
        for button in reversed(self.buttons):
            button()

        # Call every subsystem's periodic method
        for subsystem in self.subsystems:
            subsystem.periodic()

        # Loop through the commands
        for command in list(self.commandTable):
            if not command.run():
                self.remove(command)
                self.runningCommandsChanged = True

        # Add the new things
        for command in self.additions:
            self._add(command)
        self.additions.clear()

        # Add in the defaults
        for lock in self.subsystems:
            if lock.getCurrentCommand() is None:
                self._add(lock.getDefaultCommand())
            lock.confirmCommand()

    def registerSubsystem(self, system):
        """Registers a :class:`.Subsystem` to this Scheduler, so that the
        Scheduler might know if a default Command needs to be
        run. All :class:`.Subsystem` objects should call this.

        :param system: the system
        """
        if system is not None:
            self.subsystems.add(system)

    def remove(self, command):
        """Removes the :class:`.Command` from the Scheduler.

        :param command: the command to remove
        """
        if command is None or command not in self.commandTable:
            return
        del self.commandTable[command]
        for reqt in command.getRequirements():
            reqt.setCurrentCommand(None)
        command.removed()

    def removeAll(self):
        """Removes all commands
        """
        # TODO: Confirm that this works with "uninteruptible" commands
        for command in self.commandTable:
            for reqt in command.getRequirements():
                reqt.setCurrentCommand(None)
            command.removed()
        self.commandTable.clear()

    def disable(self):
        """Disable the command scheduler.
        """
        self.disabled = True

    def enable(self):
        """Enable the command scheduler.
        """
        self.disabled = False

    def initSendable(self, builder):
        builder.setSmartDashboardType("Scheduler")
        self.namesEntry = builder.getEntry("Names")
        self.idsEntry = builder.getEntry("Ids")
        self.cancelEntry = builder.getEntry("Cancel")
        builder.setUpdateTable(self._updateTable)

    def _updateTable(self):
        if not (
            self.namesEntry is not None
            and self.idsEntry is not None
            and self.cancelEntry is not None
        ):
            return

        toCancel = self.cancelEntry.getDoubleArray([])
        if toCancel:
            for command in self.commandTable:
                if float(id(command)) in toCancel:
                    command.cancel()
            self.cancelEntry.setDoubleArray([])

        if self.runningCommandsChanged:
            commands = []
            ids = []

            for command in self.commandTable:
                commands.append(command.getName())
                ids.append(id(command))

            self.namesEntry.setStringArray(commands)
            self.idsEntry.setDoubleArray(ids)
