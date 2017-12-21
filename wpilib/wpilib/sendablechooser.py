# validated: 2017-12-16 EN f9bece2ffbf7 edu/wpi/first/wpilibj/smartdashboard/SendableChooser.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .sendablebase import SendableBase

__all__ = ["SendableChooser"]

class SendableChooser(SendableBase):
    """A useful tool for presenting a selection of options to be displayed on
    the :class:`.SmartDashboard`

    For instance, you may wish to be able to select between multiple
    autonomous modes. You can do this by putting every possible :class:`.Command`
    you want to run as an autonomous into a SendableChooser and then put
    it into the :class:`.SmartDashboard` to have a list of options appear on the
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
        super().__init__()
        self.map = {}
        self.tableSelected = None
        self.defaultChoice = ""

    def addObject(self, name, object):
        """Adds the given object to the list of options. On the
        :class:`.SmartDashboard` on the desktop, the object will appear as the
        given name.

        :param name: the name of the option
        :param object: the option
        """
        self.map[name] = object

    def addDefault(self, name, object):
        """Add the given object to the list of options and marks it as the
        default.  Functionally, this is very close to :meth:`.addObject` except
        that it will use this as the default option if none other is
        explicitly selected.

        :param name: the name of the option
        :param object: the option
        """
        if name is None:
            raise ValueError("Name cannot be None")
        self.defaultChoice = name
        self.addObject(name, object)

    def getSelected(self):
        """Returns the object associated with the selected option. If there
        is none selected, it will return the default. If there is none
        selected and no default, then it will return None.

        :returns: the object associated with the selected option
        """
        selected = self.defaultChoice
        if self.tableSelected is not None:
            selected = self.tableSelected.getString(self.defaultChoice)
        return self.map.get(selected)

    def initSendable(self, builder):
        builder.setSmartDashboardType("String Chooser")
        builder.addStringProperty(self.DEFAULT, lambda: self.defaultChoice, None)
        builder.addStringArrayProperty(self.OPTIONS, lambda: self.map.keys(), None)
        self.tableSelected = builder.getEntry(self.SELECTED)
