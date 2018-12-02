# validated: 2018-10-30 EN 0b113ad9ce93 edu/wpi/first/wpilibj/command/Command.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .scheduler import Scheduler
from ..robotstate import RobotState
from ..sendablebase import SendableBase
from ..timer import Timer
from networktables import NetworkTables

import threading

__all__ = ["Command"]


class Command(SendableBase):
    """The Command class is at the very core of the entire command framework.
    Every command can be started with a call to start().
    Once a command is started it will call :meth:`initialize`, and then
    will repeatedly call :meth:`execute` until :meth:`isFinished` returns True.
    Once it does, :meth:`end` will be called.
    
    However, if at any point while it is running :meth:`cancel` is called, then
    the command will be stopped and :meth:`interrupted` will be called.
    
    If a command uses a :class:`.Subsystem`, then it should specify that it
    does so by calling the :meth:`requires` method in its constructor.
    Note that a Command may have multiple requirements, and :meth:`requires`
    should be called for each one.
    
    If a command is running and a new command with shared requirements is
    started, then one of two things will happen.  If the active command is
    interruptible, then :meth:`cancel` will be called and the command will be removed
    to make way for the new one.  If the active command is not interruptible,
    the other one will not even be started, and the active one will continue
    functioning.
    
    .. seealso:: :class:`.Subsystem`, :class:`.CommandGroup`
    """

    def __init__(self, name=None, timeout=None, subsystem=None):
        """Creates a new command.
        
        :param name: The name for this command; if unspecified or None,
                     The name of this command will be set to its class name.
        :param timeout: The time (in seconds) before this command "times out".
                        Default is no timeout.  See isTimedOut().
        :param subsystem: The subsystem that this command requires
        """
        super().__init__(False)
        self.mutex = threading.RLock()

        # The name of this command
        if name is None:
            name = self.__class__.__name__

        self.setName(name)

        # The time (in seconds) before this command "times out" (or None if no
        # timeout)
        if timeout is not None and timeout < 0:
            raise ValueError("Timeout must not be negative")
        if timeout is None:
            timeout = -1.0
        self.timeout = timeout

        # The time since this command was initialized
        self.startTime = None
        # Whether or not this command has been initialized
        self.initialized = False
        # The required subsystems.
        self.requirements = set()
        # Whether or not it is running
        self.running = False
        # Whether or not this command has completed running
        self.completed = True
        # Whether or not it is interruptible
        self.interruptible = True
        # Whether or not it has been canceled
        self.canceled = False
        # Whether or not it has been locked
        self.locked = False
        # Whether this command should run when the robot is disabled
        self.runWhenDisabled = False
        # The CommandGroup this is in
        self.parent = None

        if subsystem is not None:
            self.requires(subsystem)

    def setTimeout(self, seconds):
        """Sets the timeout of this command.
        
        :param seconds: the timeout (in seconds)
        
        :see: :meth:`isTimedOut`
        """
        if seconds < 0:
            raise ValueError("Seconds must be positive.")
        with self.mutex:
            self.timeout = seconds

    def timeSinceInitialized(self):
        """Returns the time since this command was initialized (in seconds).
        This function will work even if there is no specified timeout.
        
        :returns: the time since this command was initialized (in seconds).
        """
        with self.mutex:
            if self.startTime is None:
                return 0
            else:
                return Timer.getFPGATimestamp() - self.startTime

    def requires(self, subsystem):
        """This method specifies that the given Subsystem is used by this
        command.  This method is crucial to the functioning of the Command
        System in general.

        Note that the recommended way to call this method is in the
        constructor.

        :param subsystem: the :class:`.Subsystem` required
        """
        with self.mutex:
            if self.locked:
                raise ValueError("Can not add new requirement to command")
            if subsystem is None:
                raise ValueError("Subsystem must not be None.")
            self.requirements.add(subsystem)

    def removed(self):
        """Called when the command has been removed. This will call
        :meth:`interrupted` or :meth:`end`.
        """
        with self.mutex:
            if self.initialized:
                if self.isCanceled():
                    self.interrupted()
                    self._interrupted()
                else:
                    self.end()
                    self._end()
            self.initialized = False
            self.canceled = False
            self.running = False
            self.completed = True

    def run(self):
        """The run method is used internally to actually run the commands.
        
        :returns: whether or not the command should stay within the Scheduler.
        """
        with self.mutex:
            if (
                not self.runWhenDisabled
                and self.parent is None
                and RobotState.isDisabled()
            ):
                self.cancel()
            if self.isCanceled():
                return False
            if not self.initialized:
                self.initialized = True
                self.startTiming()
                self._initialize()
                self.initialize()
            self._execute()
            self.execute()
            return not self.isFinished()

    def initialize(self):
        """The initialize method is called the first time this Command is run
        after being started.
        """
        pass

    def _initialize(self):
        """A shadow method called before initialize()."""
        pass

    def execute(self):
        """The execute method is called repeatedly until this Command either
        finishes or is canceled.
        """
        pass

    def _execute(self):
        """A shadow method called before execute()."""
        pass

    def isFinished(self):
        """Returns whether this command is finished.
        If it is, then the command will be removed and end() will be called.

        It may be useful for a team to reference the isTimedOut() method
        for time-sensitive commands, or override TimedCommand.

        If you do not specify isFinished in your command, the command will only
        end if interrupted or canceled. If you want a command that executes only
        once and then ends, override InstantCommand.

        :returns: whether this command is finished.
        :see: :meth:`isTimedOut`
        :see: :class: `.TimedCommand`
        :see: :class: `.InstantCommand`
        """
        return False

    def end(self):
        """Called when the command ended peacefully.  This is where you may
        want to wrap up loose ends, like shutting off a motor that was being
        used in the command.
        """
        pass

    def _end(self):
        """A shadow method called after end()."""
        pass

    def interrupted(self):
        """Called when the command ends because somebody called cancel() or
        another command shared the same requirements as this one, and booted
        it out.

        This is where you may want to wrap up loose ends, like shutting off a
        motor that was being used in the command.

        Generally, it is useful to simply call the end() method within this
        method, as done here.
        """
        self.end()

    def _interrupted(self):
        """A shadow method called after interrupted()."""
        pass

    def startTiming(self):
        """Called to indicate that the timer should start.
        This is called right before initialize() is, inside the run() method.
        """
        with self.mutex:
            self.startTime = Timer.getFPGATimestamp()

    def isTimedOut(self):
        """Returns whether or not the :meth:`timeSinceInitialized` method returns a
        number which is greater than or equal to the timeout for the command.
        If there is no timeout, this will always return false.
        
        :returns: whether the time has expired
        """
        with self.mutex:
            return self.timeout != -1 and self.timeSinceInitialized() >= self.timeout

    def getRequirements(self):
        """Returns the requirements (as a set of Subsystems) of this command
        """
        with self.mutex:
            return self.requirements.copy()

    def lockChanges(self):
        """Prevents further changes from being made
        """
        with self.mutex:
            self.locked = True

    def setParent(self, parent):
        """Sets the parent of this command.  No actual change is made to the
        group.

        :param parent: the parent
        """
        with self.mutex:
            if self.parent is not None:
                raise ValueError(
                    "Can not give command to a command group after already being put in a command group"
                )
            self.lockChanges()
            self.parent = parent

    def isParented(self):
        """
        Returns whether the command has a parent.

        :returns: True if the command has a parent.
        """
        with self.mutex:
            return self.parent is not None

    def clearRequirements(self):
        """Clears list of subsystem requirements. This is only used by
        :class:`.ConditionalCommand` so cancelling the chosen command works properly
        in :class:`.CommandGroup`.
        """
        self.requirements.clear()

    def start(self):
        """Starts up the command.  Gets the command ready to start.
        Note that the command will eventually start, however it will not
        necessarily do so immediately, and may in fact be canceled before
        initialize is even called.
        """
        with self.mutex:
            self.lockChanges()
            if self.parent is not None:
                raise ValueError(
                    "Can not start a command that is a part of a command group"
                )
            Scheduler.getInstance().add(self)
            self.completed = False

    def startRunning(self):
        """This is used internally to mark that the command has been started.
        The lifecycle of a command is:

        * :meth:`startRunning` is called.
        * :meth:`run` is called (multiple times potentially)
        * :meth:`removed` is called

        It is very important that :meth:`startRunning` and :meth:`removed` be
        called in order or some assumptions of the code will be broken.
        """
        with self.mutex:
            self.running = True
            self.startTime = None

    def isRunning(self):
        """Returns whether or not the command is running.
        This may return true even if the command has just been canceled, as it
        may not have yet called :meth:`interrupted`.
        
        :returns: whether or not the command is running
        """
        with self.mutex:
            return self.running

    def cancel(self):
        """This will cancel the current command.

        This will cancel the current command eventually.  It can be called
        multiple times.  And it can be called when the command is not running.
        If the command is running though, then the command will be marked as
        canceled and eventually removed.

        .. warning:: A command can not be canceled if it is a part of a
                    :class:`.CommandGroup`, you must cancel the CommandGroup
                    instead.
        """
        if self.parent is not None:
            raise ValueError("Can not manually cancel a command in a command group")
        self._cancel()

    def _cancel(self):
        """This works like cancel(), except that it doesn't throw an exception
        if it is a part of a command group.  Should only be called by the
        parent command group.
        """
        with self.mutex:
            if self.isRunning():
                self.canceled = True

    def isCanceled(self):
        """Returns whether or not this has been canceled.
        
        :returns: whether or not this has been canceled
        """
        with self.mutex:
            return self.canceled

    def isCompleted(self) -> bool:
        """Whether or not this command has completed running.
        
        :returns: whether or not this command has completed running.
        """
        with self.mutex:
            return self.completed

    def isInterruptible(self):
        """Returns whether or not this command can be interrupted.
        
        :returns: whether or not this command can be interrupted
        """
        with self.mutex:
            return self.interruptible

    def setInterruptible(self, interruptible):
        """Sets whether or not this command can be interrupted.
        
        :param interruptible: whether or not this command can be interrupted
        """
        with self.mutex:
            self.interruptible = interruptible

    def doesRequire(self, system):
        """Checks if the command requires the given :class:`.Subsystem`.
        
        :param system: the system
        :returns: whether or not the subsystem is required, or False if given
                  None.
        """
        with self.mutex:
            return system in self.requirements

    def getGroup(self):
        """Returns the :class:`.CommandGroup` that this command is a part of.
        Will return None if this Command is not in a group.
        
        :returns: the :class:`.CommandGroup` that this command is a part of
                  (or None if not in group)
        """
        with self.mutex:
            return self.parent

    def setRunWhenDisabled(self, run):
        """Sets whether or not this {@link Command} should run when the robot
        is disabled.

        By default a command will not run when the robot is disabled, and will
        in fact be canceled.

        :param run: whether or not this command should run when the robot is
                    disabled
        """
        with self.mutex:
            self.runWhenDisabled = run

    def willRunWhenDisabled(self):
        """Returns whether or not this Command will run when the robot is
        disabled, or if it will cancel itself.
        """
        with self.mutex:
            return self.runWhenDisabled

    def __str__(self):
        """The string representation for a Command is by default its name.
        
        :returns: the string representation of this object
        """
        return self.getName()

    def runningChanged(self, value):
        if value:
            if not self.isRunning():
                self.start()
        else:
            if self.isRunning():
                self.cancel()

    def initSendable(self, builder):
        builder.setSmartDashboardType("Command")
        builder.addStringProperty(".name", self.getName, None)
        builder.addBooleanProperty("running", self.isRunning, self.runningChanged)
        builder.addBooleanProperty(".isParented", self.isParented, None)
