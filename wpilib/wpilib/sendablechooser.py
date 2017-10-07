# validated: 2017-10-07 EN 34c18ef00062 edu/wpi/first/wpilibj/smartdashboard/SendableChooser.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
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
        chooser.addObject('option1', '1')
        chooser.addObject('option2', '2')

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
        self.map = {}
        self.defaultChoice = None

    def addObject(self, name, object):
        """Adds the given object to the list of options. On the
        SmartDashboard on the desktop, the object will appear as the
        given name.

        :param name: the name of the option
        :param object: the option
        """
        self.map[name] = object

        if self.tableOptions is not None:
            self.tableOptions.setStringArray(self.map.keys())

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
        if self.tableDefault is not None:
            self.tableDefault.setString(self.defaultChoice)
        self.addObject(name, object)

    def getSelected(self):
        """Returns the object associated with the selected option. If there
        is none selected, it will return the default. If there is none
        selected and no default, then it will return None.

        :returns: the object associated with the selected option
        """
        selected = self.tableSelected.getString(None)
        return self.map.get(selected, self.map[self.defaultChoice])

    def getSmartDashboardType(self):
        return "String Chooser"

    def initTable(self, table):
        if table is not None:
            self.tableDefault = table.getEntry(self.DEFAULT)
            self.tableSelected = table.getEntry(self.SELECTED)
            self.tableOptions = table.getEntry(self.OPTIONS)
            self.tableOptions.setStringArray(self.map.keys())
            if self.defaultChoice is not None:
                self.tableDefault.setString(self.defaultChoice)
