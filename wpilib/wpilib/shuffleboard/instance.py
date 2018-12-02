# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardInstance.java
from .tab import ShuffleboardTab
from .root import ShuffleboardRoot
from .complexwidget import ComplexWidget
from .container import ShuffleboardContainer


class ShuffleboardInstance(ShuffleboardRoot):
    def __init__(self, ntInstance):
        from .shuffleboard import Shuffleboard

        assert ntInstance is not None, "NetworkTable instance cannot be None"
        self.rootTable = ntInstance.getTable(Shuffleboard.kBaseTableName)
        self.rootMetaTable = self.rootTable.getSubTable(".metadata")
        self.tabsChanged = False
        self.tabs = {}

    def getTab(self, title: str) -> "ShuffleboardTab":
        assert title is not None, "Tab title cannot be None"
        if title not in self.tabs:
            self.tabs[title] = ShuffleboardTab(self, title)
            self.tabsChanged = True
        return self.tabs[title]

    def update(self):
        if self.tabsChanged:
            tabTitles = [tab.getTitle() for tab in self.tabs.values()]
            self.rootMetaTable.getEntry("Tabs").forceSetStringArray(tabTitles)
            self.tabsChanged = False

        for tab in self.tabs.values():
            title = tab.getTitle()
            tab.buildInto(self.rootTable, self.rootMetaTable.getSubTable(title))

    def enableActuatorWidgets(self):
        self._applyToAllComplexWidgets(lambda c: c.enableIfActuator())

    def disableActuatorWidgets(self):
        self._applyToAllComplexWidgets(lambda c: c.disableIfActuator())

    def _applyToAllComplexWidgets(self, func):
        """
        Applies the function `func` to all complex widgets in this root, 
        regardless of how they are nested.

        :param func: the function to apply to all complex widgets
        """
        for tab in self.tabs.values():
            self._apply(tab, func)

    def _apply(self, container, func):
        """
        Applies the function `func` to all complex widgets in `container`. 
        Helper method for :class:`._applyToAllComplexWidgets`.

        """
        for component in container.getComponents():
            if isinstance(component, ComplexWidget):
                func(component)
            if isinstance(component, ShuffleboardContainer):
                self._apply(component, func)
