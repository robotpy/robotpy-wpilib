# validated: 2017-01-13 DS 7a049c29bdb7 shared/java/edu/wpi/first/wpilibj/command/ConditionalCommand.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2017 All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .command import Command
from .instantcommand import InstantCommand

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

        if onTrue is None:
            onTrue = InstantCommand(None)
        if onFalse is None:
            onFalse = InstantCommand(None)
            
        self.onTrue = onTrue
        self.onFalse = onFalse
        
        self.chosenCommand = None
        
        for e in onTrue.getRequirements():
            self.requires(e)
            
        for e in onFalse.getRequirements():
            self.requires(e)
    
    def condition(self):
        """The Condition to test to determine which Command to run.
        
        :returns: true if m_onTrue should be run or false if m_onFalse should be run.
        """
        raise NotImplementedError
    
    def _initialize(self):
        '''
            Calls condition() and runs the proper command.
        '''
        if self.condition():
            self.chosenCommand = self.onTrue
        else:
            self.chosenCommand = self.onFalse
            
        # This is a hack to make cancelling the chosen command inside a CommandGroup work properly
        self.chosenCommand.clearRequirements()
        
        self.chosenCommand.start()
    
    def _cancel(self):
        if self.chosenCommand is not None and self.chosenCommand.isRunning():
            self.chosenCommand.cancel()
            
        super()._cancel()
    
    def isFinished(self):
        return self.chosenCommand is not None and self.chosenCommand.isRunning() and \
            self.chosenCommand.isFinished()
    
    def interrupted(self):
        if self.chosenCommand is not None and self.chosenCommand.isRunning():
            self.chosenCommand.cancel()
            
        super().interrupted()
