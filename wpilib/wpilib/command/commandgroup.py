# validated: 2017-10-03 EN e1195e8b9dab edu/wpi/first/wpilibj/command/CommandGroup.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .command import Command

__all__ = ["CommandGroup"]


class CommandGroup(Command):
    """A CommandGroup is a list of commands which are executed in sequence.

    Commands in a CommandGroup are added using the :meth:`addSequential` method
    and are called sequentially. CommandGroups are themselves Commands and can
    be given to other CommandGroups.

    CommandGroups will carry all of the requirements of their subcommands.
    Additional requirements can be specified by calling :meth:`requires`
    normally in the constructor.

    CommandGroups can also execute commands in parallel, simply by adding them
    using addParallel(...).

    .. seealso:: :class:`.Command`, :class:`Subsystem`
    """

    class Entry:
        IN_SEQUENCE = 0
        BRANCH_PEER = 1
        BRANCH_CHILD = 2

        def __init__(self, command, state, timeout):
            self.command = command
            self.state = state
            self.timeout = timeout

        def isTimedOut(self):
            if self.timeout is None:
                return False
            else:
                time = self.command.timeSinceInitialized()
                if time == 0:
                    return False
                else:
                    return time >= self.timeout

    def __init__(self, name=None):
        """Creates a new CommandGroup with the given name.
        
        :param name: the name for this command group (optional).  If None,
                     the name of this command will be set to its class name.
        """
        super().__init__(name)
        # The commands in this group (stored in entries)
        self.commands = []
        # The active children in this group (stored in entries)
        self.children = []
        # The current command, None signifies that none have been run
        self.currentCommandIndex = None

    def addSequential(self, command, timeout=None):
        """Adds a new Command to the group (with an optional timeout).
        The Command will be started after all the previously added Commands.

        Once the Command is started, it will be run until it finishes or the
        time expires, whichever is sooner (if a timeout is provided).  Note
        that the given Command will have no knowledge that it is on a timer.

        Note that any requirements the given Command has will be added to the
        group.  For this reason, a Command's requirements can not be changed
        after being added to a group.

        It is recommended that this method be called in the constructor.

        :param command: The Command to be added
        :param timeout: The timeout (in seconds) (optional)
        """
        with self.mutex:
            if self.locked:
                raise ValueError("Can not add new command to command group")
            if command is None:
                raise ValueError("Given None command")
            if timeout is not None and timeout < 0:
                raise ValueError("Can not be given a negative timeout")

            command.setParent(self)

            self.commands.append(
                CommandGroup.Entry(command, CommandGroup.Entry.IN_SEQUENCE, timeout)
            )
            for reqt in command.getRequirements():
                self.requires(reqt)

    def addParallel(self, command, timeout=None):
        """Adds a new child Command to the group (with an optional timeout).
        The Command will be started after all the previously added Commands.

        Once the Command is started, it will run until it finishes, is
        interrupted, or the time expires (if a timeout is provided), whichever
        is sooner.  Note that the given Command will have no knowledge that it
        is on a timer.

        Instead of waiting for the child to finish, a CommandGroup will have it
        run at the same time as the subsequent Commands.  The child will run
        until either it finishes, the timeout expires, a new child with
        conflicting requirements is started, or the main sequence runs a
        Command with conflicting requirements.  In the latter two cases, the
        child will be canceled even if it says it can't be interrupted.

        Note that any requirements the given Command has will be added to the
        group.  For this reason, a Command's requirements can not be changed
        after being added to a group.

        It is recommended that this method be called in the constructor.

        :param command: The command to be added
        :param timeout: The timeout (in seconds) (optional)
        """
        with self.mutex:
            if command is None:
                raise ValueError("Given null command")
            if timeout is not None and timeout < 0:
                raise ValueError("Can not be given a negative timeout")
            if self.locked:
                raise ValueError("Can not add new command to command group")

            command.setParent(self)

            self.commands.append(
                CommandGroup.Entry(command, CommandGroup.Entry.BRANCH_CHILD, timeout)
            )
            for reqt in command.getRequirements():
                self.requires(reqt)

    def _initialize(self):
        self.currentCommandIndex = None

    def _execute(self):
        entry = None
        cmd = None
        firstRun = False
        if self.currentCommandIndex is None:
            firstRun = True
            self.currentCommandIndex = 0

        while self.currentCommandIndex < len(self.commands):
            if cmd is not None:
                if entry.isTimedOut():
                    cmd._cancel()
                if cmd.run():
                    break
                else:
                    cmd.removed()
                    self.currentCommandIndex += 1
                    firstRun = True
                    cmd = None
                    continue

            entry = self.commands[self.currentCommandIndex]
            cmd = None

            if entry.state == CommandGroup.Entry.IN_SEQUENCE:
                cmd = entry.command
                if firstRun:
                    cmd.startRunning()
                    self.cancelConflicts(cmd)
                firstRun = False
            elif entry.state == CommandGroup.Entry.BRANCH_PEER:
                self.currentCommandIndex += 1
                entry.command.start()
            elif entry.state == CommandGroup.Entry.BRANCH_CHILD:
                self.currentCommandIndex += 1
                self.cancelConflicts(entry.command)
                entry.command.startRunning()
                self.children.append(entry)

        # Run Children
        toremove = []
        for i, entry in enumerate(self.children):
            child = entry.command
            if entry.isTimedOut():
                child._cancel()
            if not child.run():
                child.removed()
                toremove.append(i)
        for i in reversed(toremove):
            del self.children[i]

    def _end(self):
        # Theoretically, we don't have to check this, but we do if teams
        # override the isFinished method
        if self.currentCommandIndex is not None and self.currentCommandIndex < len(
            self.commands
        ):
            cmd = self.commands[self.currentCommandIndex].command
            cmd._cancel()
            cmd.removed()

        for entry in self.children:
            cmd = entry.command
            cmd._cancel()
            cmd.removed()
        self.children.clear()

    def _interrupted(self):
        self._end()

    def isFinished(self):
        """Returns True if all the Commands in this group
        have been started and have finished.

        Teams may override this method, although they should probably
        reference super().isFinished() if they do.

        :returns: whether this CommandGroup is finished
        """
        if self.currentCommandIndex is None:
            return False
        return self.currentCommandIndex >= len(self.commands) and not self.children

    def initialize(self):
        pass  # Can be overwritten by teams

    def execute(self):
        pass  # Can be overwritten by teams

    def end(self):
        pass  # Can be overwritten by teams

    def interrupted(self):
        pass  # Can be overwritten by teams

    def isInterruptible(self):
        """Returns whether or not this group is interruptible.
        A command group will be uninterruptible if setInterruptable(False)
        was called or if it is currently running an uninterruptible command
        or child.

        :returns: whether or not this CommandGroup is interruptible.
        """
        with self.mutex:
            if not super().isInterruptible():
                return False

            if self.currentCommandIndex is not None and self.currentCommandIndex < len(
                self.commands
            ):
                cmd = self.commands[self.currentCommandIndex].command
                if not cmd.isInterruptible():
                    return False

            for entry in self.children:
                if not entry.command.isInterruptible():
                    return False

        return True

    def cancelConflicts(self, command):
        toremove = []
        for i, entry in enumerate(self.children):
            child = entry.command

            for requirement in command.getRequirements():
                if child.doesRequire(requirement):
                    child._cancel()
                    child.removed()
                    toremove.append(i)
                    break

        for i in reversed(toremove):
            del self.children[i]
