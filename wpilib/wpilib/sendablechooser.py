#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .sendable import Sendable

__all__ = ["SendableChooser"]

class SendableChooser(Sendable):
    """A useful tool for presenting a selection of options to be displayed on
    the SmartDashboard

    For instance, you may wish to be able to select between multiple
    autonomous modes. You can do this by putting every possible Command
    you want to run as an autonomous into a SendableChooser and then put
    it into the SmartDashboard to have a list of options appear on the
    laptop. Once autonomous starts, simply ask the SendableChooser what
    the selected value is.
    
    Example::
    
        # This shows the user two options on the SmartDashboard
        chooser = wpilib.SendableChooser()
        chooser.addOption('option1', '1')
        chooser.addOption('option2', '2')
        
        wpilib.SmartDashboard.putData('Choice', chooser)
        
        # .. later, ask to see what the user selected?
        value = chooser.getSelected()
    
    """

    # The key for the default value
    DEFAULT = "default"
    # The key for the selected option
    SELECTED = "selected"
    # The key for the option array
    OPTIONS = "options"
    # A table linking strings to the objects the represent

    def __init__(self):
        """Instantiates a SendableChooser.
        """
        from networktables import StringArray
        self.choices = StringArray()
        self.values = []
        self.defaultChoice = None
        self.defaultValue = None

    def addObject(self, name, object):
        """Adds the given object to the list of options. On the
        SmartDashboard on the desktop, the object will appear as the
        given name.

        :param name: the name of the option
        :param object: the option
        """
        # if we don't have a default, set the default automatically
        if self.defaultChoice is None:
            self.addDefault(name, object)
            return
        for i, choice in enumerate(self.choices):
            if choice == name:
                self.values[i] = object
                return
        # not found
        self.choices.append(name)
        self.values.append(object)
        table = self.getTable()
        if table is not None:
            table.putValue(self.OPTIONS, self.choices)

    def addDefault(self, name, object):
        """Add the given object to the list of options and marks it as the
        default.  Functionally, this is very close to addObject(...) except
        that it will use this as the default option if none other is
        explicitly selected.

        :param name: the name of the option
        :param object: the option
        """
        if name is None:
            raise ValueError("Name cannot be None")
        self.defaultChoice = name
        self.defaultValue = object
        table = self.getTable()
        if table is not None:
            table.putString(self.DEFAULT, self.defaultChoice)
        self.addObject(name, object)

    def getSelected(self):
        """Returns the object associated with the selected option. If there
        is none selected, it will return the default. If there is none
        selected and no default, then it will return None.

        :returns: the object associated with the selected option
        """
        table = self.getTable()
        if table is None:
            return self.defaultValue
        selected = table.getString(self.SELECTED, None)
        for i, choice in enumerate(self.choices):
            if choice == selected:
                return self.values[i]
        return self.defaultValue

    def getSmartDashboardType(self):
        return "String Chooser"

    def initTable(self, table):
        self.table = table
        if table is not None:
            table.putValue(self.OPTIONS, self.choices)
            if self.defaultChoice is not None:
                table.putString(self.DEFAULT, self.defaultChoice)
