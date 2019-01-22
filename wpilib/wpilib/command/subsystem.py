# validated: 2018-09-09 EN b7807bf9d26e edu/wpi/first/wpilibj/command/Subsystem.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import logging
from typing import Optional

from ..livewindow import LiveWindow
from .scheduler import Scheduler
from ..sendablebase import SendableBase
from ..sendablebuilder import SendableBuilder

from . import command
from .. import sendable

__all__ = ["Subsystem"]


class Subsystem(SendableBase):
    """This class defines a major component of the robot.

    A good example of a subsystem is the driveline, or a claw if the robot has
    one.

    All motors should be a part of a subsystem. For instance, all the wheel
    motors should be a part of some kind of "Driveline" subsystem.

    Subsystems are used within the command system as requirements for Command.
    Only one command which requires a subsystem can run at a time.  Also,
    subsystems can have default commands which are started if there is no
    command running which requires this subsystem.

    .. seealso:: :class:`.Command`
    """

    def __init__(self, name: Optional[str] = None) -> None:
        """Creates a subsystem.

        :param name: the name of the subsystem; if None, it will be set to the
                     name to the name of the class.
        """
        super().__init__()
        # The name
        if name is None:
            name = self.__class__.__name__
        self.setName(name)

        Scheduler.getInstance().registerSubsystem(self)
        self.logger = logging.getLogger(__name__)

        # Whether or not getDefaultCommand() was called
        self.initializedDefaultCommand = False
        # The current command
        self.currentCommand = None
        self.currentCommandChanged = True

        # The default command
        self.defaultCommand = None

    def initDefaultCommand(self) -> None:
        """Initialize the default command for a subsystem
        By default subsystems have no default command, but if they do, the
        default command is set with this method. It is called on all
        Subsystems by CommandBase in the users program after all the
        Subsystems are created.
        """
        pass

    def periodic(self) -> None:
        """When the run method of the scheduler is called this method will be called.
        """
        func = self.periodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default Subsystem.periodic() method... Override me!")
            func.firstRun = False

    def setDefaultCommand(self, command: "command.Command") -> None:
        """Sets the default command.  If this is not called or is called with
        None, then there will be no default command for the subsystem.

        :param command: the default command (or None if there should be none)
        
        .. warning:: This should NOT be called in a constructor if the subsystem
                     is a singleton.
        """
        if command is None:
            self.defaultCommand = None
        else:
            if self not in command.getRequirements():
                raise ValueError("A default command must require the subsystem")
            self.defaultCommand = command

    def getDefaultCommand(self) -> "command.Command":
        """Returns the default command (or None if there is none).
        
        :returns: the default command
        """
        if not self.initializedDefaultCommand:
            self.initializedDefaultCommand = True
            self.initDefaultCommand()
        return self.defaultCommand

    def getDefaultCommandName(self) -> str:
        """
        Returns the default command name, or empty string is there is none.

        :returns: the default command name
        """
        defaultCommand = self.getDefaultCommand()
        if defaultCommand is not None:
            return defaultCommand.getName()
        return ""

    def setCurrentCommand(self, command: Optional["command.Command"]) -> None:
        """Sets the current command
        
        :param command: the new current command
        """
        self.currentCommand = command
        self.currentCommandChanged = True

    def confirmCommand(self) -> None:
        """Call this to alert Subsystem that the current command is actually
        the command.  Sometimes, the Subsystem is told that it has no command
        while the Scheduler is going through the loop, only to be soon after
        given a new one.  This will avoid that situation.
        """
        if self.currentCommandChanged:
            self.currentCommandChanged = False

    def getCurrentCommand(self) -> "command.Command":
        """Returns the command which currently claims this subsystem.
        
        :returns: the command which currently claims this subsystem
        """
        return self.currentCommand

    def getCurrentCommandName(self) -> str:
        """
        Returns the current command name, or empty string if no current command.

        :returns: the current command name
        """
        currentCommand = self.getCurrentCommand()
        if currentCommand is not None:
            return currentCommand.getName()
        return ""

    def addChild(self, child: "sendable.Sendable", name: Optional[str] = None) -> None:
        """
        Associate a :class:`.Sendable` with this Subsystem.
        Update the child's name if provided

        :param child: sendable
        :param name: name to give child
        """
        if name is not None:
            child.setName(self.getSubsystem(), name)
        else:
            child.setSubsystem(self.getSubsystem())
        LiveWindow.add(child)

    def __str__(self) -> str:
        return self.getSubsystem()

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Subsystem")
        builder.addBooleanProperty(
            ".hasDefault", lambda: self.defaultCommand is not None, None
        )
        builder.addStringProperty(".default", self.getDefaultCommandName, None)
        builder.addBooleanProperty(
            ".hasCommand", lambda: self.defaultCommand is not None, None
        )
        builder.addStringProperty(".command", self.getCurrentCommandName, None)
