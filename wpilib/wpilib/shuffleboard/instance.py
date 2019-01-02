# validated: 2018-12-15 EN 6f0c185a05c9 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardInstance.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .tab import ShuffleboardTab
from .root import ShuffleboardRoot
from .complexwidget import ComplexWidget
from .container import ShuffleboardContainer


class ShuffleboardInstance(ShuffleboardRoot):
    def __init__(self, ntInstance) -> None:
        from .shuffleboard import Shuffleboard

        self.rootTable = ntInstance.getTable(Shuffleboard.kBaseTableName)
        self.rootMetaTable = self.rootTable.getSubTable(".metadata")
        self.selectedTabEntry = self.rootMetaTable.getEntry("Selected")
        self.tabsChanged = False
        self.tabs = {}

    def getTab(self, title: str) -> "ShuffleboardTab":
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

    def selectTab(self, index_or_title):
        if isinstance(index_or_title, int):
            self.selectedTabEntry.forceSetDouble(index_or_title)
        else:
            self.selectedTabEntry.forceSetString(index_or_title)

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
