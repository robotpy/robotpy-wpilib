# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardComponent.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .container import ShuffleboardContainer
from typing import Dict, Any, Optional


class ShuffleboardComponent:
    def __init__(
        self, parent: ShuffleboardContainer, title: str, type: Optional[str] = None
    ):
        self.parent = parent
        self.title = title
        self.type = type
        self.metadataDirty = False
        self.column = -1
        self.row = -1
        self.width = -1
        self.height = -1
        self.properties = {}  # type: Dict[str, Any]

    def getParent(self) -> ShuffleboardContainer:
        return self.parent

    def setType(self, type: str) -> None:
        self.type = type
        self.metadataDirty = True

    def getType(self) -> str:
        return self.type

    def getTitle(self) -> str:
        return self.title

    def getProperties(self) -> Dict[str, Any]:
        return self.properties

    def withProperties(self, properties: Dict[str, Any]) -> "ShuffleboardComponent":
        """
        Sets custom properties for this component. Property names are case- 
        and whitespace-insensitive (capitalization and spaces do not matter).

        :param properties: the properties for this component

        :returns: this component
        """

        self.properties = properties
        self.metadataDirty = True
        return self

    def withPosition(self, columnIndex: int, rowIndex: int) -> "ShuffleboardComponent":
        """
        Sets the position of this component in the tab. This has no effect if 
        this component is inside a layout.

        If the position of a single component is set, it is recommended to set 
        the positions of *all* components inside a tab to prevent Shuffleboard 
        from automatically placing another component there before the one with 
        the specific position is sent.

        :param columnIndex: the column in the tab to place this component
        :param rowIndex:    the row in the tab to place this component
        :returns: this component
        """
        self.column = columnIndex
        self.row = rowIndex
        self.metadataDirty = True
        return self

    def withSize(self, width: int, height: int) -> "ShuffleboardComponent":
        """
        Sets the size of this component in the tab. This has no effect if this 
        component is inside a layout.

        :param width:  how many columns wide the component should be
        :param height: how many rows high the component should be
        :returns: this component
        """
        self.width = width
        self.height = height
        self.metadataDirty = True
        return self

    def buildMetadata(self, metaTable) -> None:
        if not self.metadataDirty:
            return

        # Component type
        if self.getType() is None:
            metaTable.getEntry("PreferredComponent").delete()
        else:
            metaTable.getEntry("PreferredComponent").forceSetString(self.getType())

        # Tile size
        if self.width <= 0 or self.height <= 0:
            metaTable.getEntry("Size").delete()
        else:
            metaTable.getEntry("Size").setNumberArray((self.width, self.height))

        # Tile position
        if self.column < 0 or self.row < 0:
            metaTable.getEntry("Position").delete()
        else:
            metaTable.getEntry("Position").setNumberArray((self.column, self.row))

        # Custom properties
        if self.getProperties():
            propTable = metaTable.getSubTable("Properties")
            for name, value in self.getProperties().items():
                propTable.getEntry(name).setValue(value)
        self.metadataDirty = False

    # ShuffleboardValue interface

    def buildInto(self, parentTable, metaTable) -> None:
        """Builds the entries for this value.

        :param parentTable: the table containing all the data for the parent. Values that require a
                            complex entry or table structure should call
                            ``parentTable.getSubTable(getTitle())`` to get the table to put data into.
                            Values that only use a single entry should call
                            ``parentTable.getEntry(getTitle())`` to get that entry.

        :param metaTable: the table containing all the metadata for this value and its sub-values
        """
        raise NotImplementedError
