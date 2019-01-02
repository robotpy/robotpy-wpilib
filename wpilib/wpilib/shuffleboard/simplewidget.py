# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/SimpleWidget.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from networktables.entry import NetworkTableEntry
from .widget import ShuffleboardWidget
from .container import ShuffleboardContainer
from .layout import ShuffleboardLayout


class SimpleWidget(ShuffleboardWidget):
    """A Shuffleboard widget that handles a single data point such as a number or string."""

    def __init__(self, parent: ShuffleboardContainer, title: str):
        super().__init__(parent, title)
        self.entry = None

    def getEntry(self) -> NetworkTableEntry:
        """Gets the NetworkTable entry that contains the data for this widget."""
        if self.entry is None:
            self._forceGenerate()

        return self.entry

    def buildInto(self, parentTable, metaTable) -> None:
        self.buildMetadata(metaTable)
        if self.entry is None:
            self.entry = parentTable.getEntry(self.getTitle())

    def _forceGenerate(self):
        parent = self.getParent()  # type: ShuffleboardContainer
        while isinstance(parent, ShuffleboardLayout):
            parent = parent.getParent()

        tab = parent  # type: ShuffleboardTab
        tab.getRoot().update()
