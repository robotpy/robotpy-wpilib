# validated: 2018-09-09 EN 0e9172f9a708 edu/wpi/first/wpilibj/command/ConditionalCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2017 All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .command import Command
from .instantcommand import InstantCommand

__all__ = ["ConditionalCommand"]


class ConditionalCommand(Command):
    """
        A ConditionalCommand is a :class:`.Command` that starts one of two commands.
        
        A ConditionalCommand uses m_condition to determine whether it should run m_onTrue or
        m_onFalse.
        
        A ConditionalCommand adds the proper :class:`.Command` to the :class:`.Scheduler` during
        :meth:`initialize` and then :meth:`isFinished` will
        return true once that :class:`.Command` has finished executing.
        
        If no :class:`.Command` is specified for m_onFalse, the occurrence of that condition will be a
        no-op.
        
        @see :class:`.Command`
        @see :class:`.Scheduler`
    """

    def __init__(self, name, onTrue=None, onFalse=None):
        """Creates a new ConditionalCommand with given name and onTrue and onFalse Commands.
        
        Users of this constructor should also override condition().
        
        :param name: the name for this command group
        :param onTrue: The Command to execute if {@link ConditionalCommand#condition()} returns true
        :param onFalse: The Command to execute if {@link ConditionalCommand#condition()} returns false
        """
        super().__init__(name)

        self.onTrue = onTrue
        self.onFalse = onFalse

        self.chosenCommand = None

        self.requireAll()

    def requireAll(self):
        if self.onTrue is not None:
            for e in self.onTrue.getRequirements():
                self.requires(e)

        if self.onFalse is not None:
            for e in self.onFalse.getRequirements():
                self.requires(e)

    def condition(self):
        """The Condition to test to determine which Command to run.
        
        :returns: true if m_onTrue should be run or false if m_onFalse should be run.
        """
        raise NotImplementedError

    def _initialize(self):
        """
            Calls condition() and runs the proper command.
        """
        if self.condition():
            self.chosenCommand = self.onTrue
        else:
            self.chosenCommand = self.onFalse

        if self.chosenCommand is not None:
            # This is a hack to make cancelling the chosen command inside a CommandGroup work properly
            self.chosenCommand.clearRequirements()

            self.chosenCommand.start()

        super()._initialize()

    def _cancel(self):
        with self.mutex:
            if self.chosenCommand is not None and self.chosenCommand.isRunning():
                self.chosenCommand.cancel()

            super()._cancel()

    def isFinished(self):
        if self.chosenCommand is not None:
            return self.chosenCommand.isCompleted()
        else:
            return True

    def _interrupted(self):
        if self.chosenCommand is not None and self.chosenCommand.isRunning():
            self.chosenCommand.cancel()

        super()._interrupted()
