# validated: 2019-01-05 TW 01d13220660c edu/wpi/first/wpilibj/shuffleboard/ContainerHelper.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from typing import TYPE_CHECKING, List, Optional, Union, overload

from networktables.entry import NetworkTableEntry
from .builtinlayouts import BuiltInLayouts
from ..sendable import Sendable

if TYPE_CHECKING:
    from .complexwidget import ComplexWidget
    from .simplewidget import SimpleWidget

__all__ = ["ShuffleboardContainer"]


class ShuffleboardContainer:
    """Common interface for objects that can contain shuffleboard components."""

    __slots__ = ("usedTitles", "components", "layouts")

    def __init__(self) -> None:
        self.usedTitles = set()
        self.components = []  # type: List[ShuffleboardContainer]
        self.layouts = {}

    def getComponents(self) -> "List[ShuffleboardContainer]":
        """Gets the components that are direct children of this container."""
        return self.components

    def getLayout(self, title: str, type: Optional[Union[BuiltInLayouts, str]] = None):
        """
        Gets the layout with the given type and title, creating it if it does
        not already exist at the time this method is called.

        :param title: the title of the layout
        :param type:  the type of the layout, eg "List Layout" or "Grid Layout"
        :returns: the layout
        """
        from .layout import ShuffleboardLayout

        if title not in self.layouts:
            if type is None:
                raise KeyError("No layout has been defined with the title '%s'" % title)
            if isinstance(type, BuiltInLayouts):
                type = type.value
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

    def addCamera(self, name: str, title: Optional[str] = None):
        """
        Adds a CameraServer stream widget by name.

        :param name: the name of the camera stream
        :param title: the title of the widget
        :rtype: ShuffleboardWidget
        """
        # python-specific: Rough replacement for add(VideoSource)
        from .camerawidget import CameraWidget

        if not title:
            title = name
        self._checkTitle(title)

        widget = CameraWidget(self, title, name)
        self.components.append(widget)
        return widget
