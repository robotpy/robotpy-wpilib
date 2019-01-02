# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ContainerHelper.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from typing import TYPE_CHECKING, Optional, overload

from networktables.entry import NetworkTableEntry
from ..sendable import Sendable

if TYPE_CHECKING:
    from .complexwidget import ComplexWidget
    from .simplewidget import SimpleWidget

__all__ = ["ShuffleboardContainer"]


class ShuffleboardContainer:
    """Common interface for objects that can contain shuffleboard components."""

    def __init__(self) -> None:
        self.usedTitles = set()
        self.components = []
        self.layouts = {}

    def getComponents(self):
        """Gets the components that are direct children of this container."""
        return self.components

    def getLayout(self, type: str, title: str):
        """
        Gets the layout with the given type and title, creating it if it does 
        not already exist at the time this method is called.

        :param type:  the type of the layout, eg "List" or "Grid"
        :param title: the title of the layout
        :returns: the layout
        """
        from .layout import ShuffleboardLayout

        if title not in self.layouts:
            layout = ShuffleboardLayout(self, type, title)
            self.components.append(layout)
            self.layouts[title] = layout

        return self.layouts[title]

    @overload
    def add(self, value: Sendable, *, title: Optional[str] = None) -> "ComplexWidget":
        ...

    @overload
    def add(self, *, title: str, value) -> "SimpleWidget":
        ...

    def add(self, value, *, title: Optional[str] = None):
        """
        Adds a widget to this container to display the given sendable.

        :param value: the Sendable to display, or the default value of the widget
        :param title: the title of the widget (defaults to the
                      Sendable's name if the value is Sendable)
        :returns: a widget to display the sendable data
        :rtype: ComplexWidget or SimpleWidget
        :raises ValueError: if a widget already exists in this container
                            with the given title.
        """
        if isinstance(value, Sendable):
            from .complexwidget import ComplexWidget

            if not title:
                title = value.getName()
                if not title:
                    raise ValueError("Sendable must have a name")
            self._checkTitle(title)
            widget = ComplexWidget(self, title, value)
            self.components.append(widget)
        else:
            from .simplewidget import SimpleWidget

            if not title:
                raise ValueError("A simple widget must have a title")

            self._checkTitle(title)
            self._checkNtType(value)

            widget = SimpleWidget(self, title)
            self.components.append(widget)
            widget.getEntry().setDefaultValue(value)

        return widget

    def _checkNtType(self, data) -> None:
        if not NetworkTableEntry.isValidDataType(data):
            raise TypeError("Cannot add data of type %r to Shuffleboard" % type(data))

    def _checkTitle(self, title: str) -> None:
        if title in self.usedTitles:
            raise ValueError("Title is already in use: " + title)
        self.usedTitles.add(title)

    def addPersistent(self, title: str, defaultValue):
        """
        Adds a widget to this container to display a simple piece of data.
        Unlike :meth:`.add`, the value in the widget will be saved on the
        robot and will be used when the robot program next starts rather than
        `defaultValue`.

        :param title:        the title of the widget
        :param defaultValue: the default value of the widget. note empty lists cannot be used here
        :returns: a widget to display the sendable data
        :rtype: SimpleWidget
        :raises ValueError: if a widget already exists in this container
                            with the given title.

        .. seealso:: :meth:`.add`
        """
        widget = self.add(title=title, value=defaultValue)
        widget.getEntry().setPersistent()
        return widget
