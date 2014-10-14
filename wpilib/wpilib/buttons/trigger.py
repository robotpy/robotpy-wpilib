#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

class Trigger:
    """This class provides an easy way to link commands to inputs.

    It is very easy to link a button to a command.  For instance, you could
    link the trigger button of a joystick to a "score" command.

    It is encouraged that teams write a subclass of Trigger if they want to
    have something unusual (for instance, if they want to react to the user
    holding a button while the robot is reading a certain sensor input).
    For this, they only have to write the :func:`get` method to get the full
    functionality of the Trigger class.
    """
    def __init__(self):
        self.table = None

    def get(self):
        """Returns whether or not the trigger is active

        This method will be called repeatedly a command is linked to the
        Trigger.

        :returns: whether or not the trigger condition is active.
        """
        raise NotImplementedError

    def grab(self):
        """Returns whether :func:`get` return True or the internal table for
        :class:`SmartDashboard` use is pressed.
        """
        #return self.get() or (self.table is not None and self.table.isConnected() and self.table.getBoolean("pressed", False))  #FIXME make is connected work?
        return self.get() or (self.table is not None and
                              self.table.getBoolean("pressed", False))

    def whenActive(self, command):
        """Starts the given command whenever the trigger just becomes active.

        :param command: the command to start
        """
        def execute():
            if self.grab():
                if not execute.pressedLast:
                    execute.pressedLast = True
                    command.start()
            else:
                execute.pressedLast = False

        execute.pressedLast = self.grab()
        from ..command import Scheduler
        Scheduler.getInstance().addButton(execute)

    def whileActive(self, command):
        """Constantly starts the given command while the button is held.

        :func:`Command.start` will be called repeatedly while the trigger is
        active, and will be canceled when the trigger becomes inactive.

        :param command: the command to start
        """
        def execute():
            if self.grab():
                execute.pressedLast = True
                command.start()
            else:
                if execute.pressedLast:
                    execute.pressedLast = False
                    command.cancel()

        execute.pressedLast = self.grab()
        from ..command import Scheduler
        Scheduler.getInstance().addButton(execute)

    def whenInactive(self, command):
        """Starts the command when the trigger becomes inactive.

        :param command: the command to start
        """
        def execute():
            if self.grab():
                execute.pressedLast = True
            else:
                if execute.pressedLast:
                    execute.pressedLast = False
                    command.start()

        execute.pressedLast = self.grab()
        from ..command import Scheduler
        Scheduler.getInstance().addButton(execute)

    def toggleWhenActive(self, command):
        """Toggles a command when the trigger becomes active.

        :param command: the command to toggle
        """
        def execute():
            if self.grab():
                if not execute.pressedLast:
                    execute.pressedLast = True
                    if command.isRunning():
                        command.cancel()
                    else:
                        command.start()
            else:
                execute.pressedLast = False

        execute.pressedLast = self.grab()
        from ..command import Scheduler
        Scheduler.getInstance().addButton(execute)

    def cancelWhenActive(self, command):
        """Cancels a command when the trigger becomes active.

        :param command: the command to cancel
        """
        def execute():
            if self.grab():
                if not execute.pressedLast:
                    execute.pressedLast = True
                    command.cancel()
            else:
                execute.pressedLast = False

        execute.pressedLast = self.grab()
        from ..command import Scheduler
        Scheduler.getInstance().addButton(execute)

    def getSmartDashboardType(self):
        """These methods continue to return the "Button" SmartDashboard type
        until we decided to create a Trigger widget type for the dashboard.
        """
        return "Button"

    def initTable(self, table):
        self.table = table
        if table is not None:
            table.putBoolean("pressed", self.get())

    def getTable(self):
        return table
