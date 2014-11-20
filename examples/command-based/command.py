from wpilib.command import Command


#This is a template Command, CommandName should, of course, be replaced by the name of your desired Command
class CommandName(Command):

    def __init__(self, name=None, timeout=None):
        """This is the constructor of the command, use this to declare subsystem dependencies"""
        #Use self.requires() here to declare subsystem dependencies
        #eg. self.requires(chassis)
        super().__init__(name, timeout)

    def initialize(self):
        """Called just before this Command runs the first time"""
        pass

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """This should return true when this command no longer needs to run execute()"""
        return False

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run"""
        pass