# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ContainerHelper.java
from networktables.entry import NetworkTableEntry
from .._impl.utils import match_arglist
from ..sendable import Sendable

__all__ = ['ShuffleboardContainer']

class ShuffleboardContainer:
    """Common interface for objects that can contain shuffleboard components."""
    def __init__(self):
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

    def add(self, *args, **kwargs) -> 'ShuffleboardWidget':
        """
        Adds a widget to this container to display the given sendable.

        raises AssertionError if a widget already exists in this container 
        with the given title

        :param title:    the title of the widget. if not provided, `sendable.getName()` is used.
        :param sendable: the sendable to display
        :param defaultValue: the default value of the widget. not to be combined with `sendable`. note empty lists cannot be used here
        :returns: a widget to display the sendable data          
        """
        title_arg = ("title", [str])
        sendable_arg = ("sendable", [Sendable])
        defaultValue_arg = ("defaultValue", [object])
        templates = [[title_arg, sendable_arg],
                     [sendable_arg],
                     [title_arg, defaultValue_arg]]
        index, results = match_arglist('ContainerHelper.add',
                args, kwargs, templates)

        if index in [0, 1]:
            from .complexwidget import ComplexWidget
            sendable = results["sendable"]
            if index == 1:
                assert not(sendable.getName() is None or sendable.getName() == ""), "Sendable must have a name"
                title = sendable.getName()
            else:
                title = results["title"]
            self.checkTitle(title)
            widget = ComplexWidget(self, title, sendable)
            self.components.append(widget)
            return widget
        elif index == 2:
            from .simplewidget import SimpleWidget
            title = results["title"]
            defaultValue = results["defaultValue"]
            assert title is not None, "title cannot be None"
            assert defaultValue is not None, "Default value cannot be None"
            self.checkTitle(title)
            self.checkNtType(defaultValue)

            widget = SimpleWidget(self, title)
            self.components.append(widget)
            widget.getEntry().setDefaultValue(defaultValue)
            return widget

    def checkNtType(self, data):
        assert NetworkTableEntry.isValidDataType(data), "Cannot add data of type%s to Shuffleboard" % (type(data),)

    def checkTitle(self, title: str) -> None:
        assert title not in self.usedTitles, "Title is already in use: %s" % (title,)
        self.usedTitles.add(title)

    def addPersistent(self, title: str, defaultValue):
        """
        Adds a widget to this container to display a simple piece of data. 
        Unlike :meth:`.add`, the value in the widget will be saved on the 
        robot and will be used when the robot program next starts rather than 
        `defaultValue`.
        
        raises AssertionError if a widget already exists in this container 
        with the given title

        see :meth:`.add`

        :param title:        the title of the widget
        :param defaultValue: the default value of the widget. note empty lists cannot be used here
        :returns: a widget to display the sendable data          
        """
        widget = self.add(title, defaultValue)
        widget.getEntry().setPersistent()
        return widget
