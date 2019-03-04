# validated: 2019-01-04 TW 0d7d880261b6 edu/wpi/first/wpilibj/smartdashboard/SendableChooser.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import hal
import threading
import warnings
from typing import Any

from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder

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
    # The key for the active option
    ACTIVE = "active"
    # The key for the option array
    OPTIONS = "options"
    # The key for the instance number
    INSTANCE = ".instance"

    _increment_lock = threading.Lock()
    _instances = 0

    def __init__(self) -> None:
        """Instantiates a SendableChooser.
        """
        super().__init__(addLiveWindow=False)
        self.map = {}
        self.selected = None
        self.defaultChoice = ""
        self.activeEntries = []
        self.mutex = threading.RLock()
        with SendableChooser._increment_lock:
            self.instance = SendableChooser._instances
            SendableChooser._instances += 1

    def addOption(self, name: str, object: Any) -> None:
        """Adds the given object to the list of options. On the
        :class:`.SmartDashboard` on the desktop, the object will appear as the
        given name.

        :param name: the name of the option
        :param object: the option
        """
        self.map[name] = object

    def addObject(self, name: str, object: Any) -> None:
        """Adds the given object to the list of options. On the
        :class:`.SmartDashboard` on the desktop, the object will appear as the
        given name.

        :param name: the name of the option
        :param object: the option

        .. deprecated:: 2019.0.0
            Use :meth:`addOption` instead
        """
        warnings.warn(
            "SendableChooser.addObject is deprecated, use addOption instead",
            category=DeprecationWarning,
            stacklevel=2,
        )
        self.addOption(name, object)

    def setDefaultOption(self, name: str, object: Any) -> None:
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
        self.addOption(name, object)

    def addDefault(self, name: str, object: Any) -> None:
        """Add the given object to the list of options and marks it as the
        default.  Functionally, this is very close to :meth:`.addObject` except
        that it will use this as the default option if none other is
        explicitly selected.

        :param name: the name of the option
        :param object: the option

        .. deprecated:: 2019.0.0
            Use :meth:`setDefaultOption` instead
        """
        warnings.warn(
            "SendableChooser.addDefault is deprecated, use setDefaultOption instead",
            category=DeprecationWarning,
            stacklevel=2,
        )
        self.setDefaultOption(name, object)

    def getSelected(self) -> Any:
        """Returns the object associated with the selected option. If there
        is none selected, it will return the default. If there is none
        selected and no default, then it will return None.

        :returns: the object associated with the selected option
        """
        with self.mutex:
            if self.selected is not None:
                return self.map.get(self.selected)
            else:
                return self.map.get(self.defaultChoice)

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("String Chooser")
        builder.getEntry(SendableChooser.INSTANCE).setDouble(self.instance)
        builder.addStringProperty(self.DEFAULT, lambda: self.defaultChoice, None)
        builder.addStringArrayProperty(self.OPTIONS, lambda: self.map.keys(), None)

        def _active_property_getter():
            with self.mutex:
                return self.selected if self.selected else self.defaultChoice

        builder.addStringProperty(SendableChooser.ACTIVE, _active_property_getter, None)

        with self.mutex:
            self.activeEntries.append(builder.getEntry(SendableChooser.ACTIVE))

        def _selected_property_setter(val):
            with self.mutex:
                self.selected = val
                for entry in self.activeEntries:
                    entry.setString(val)

        # python-specific: set local=True
        builder.addStringProperty(
            SendableChooser.SELECTED,
            None,
            _selected_property_setter,
            local=hal.isSimulation(),  # only need local updates in simulation
        )
