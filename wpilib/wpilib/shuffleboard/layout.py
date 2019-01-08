# validated: 2019-01-05 TW 01d13220660c edu/wpi/first/wpilibj/shuffleboard/ShuffleboardLayout.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from networktables.networktable import NetworkTable
from .component import ShuffleboardComponent
from .container import ShuffleboardContainer


class ShuffleboardLayout(ShuffleboardComponent, ShuffleboardContainer):
    def __init__(self, parent: ShuffleboardContainer, name: str, type: str):
        ShuffleboardComponent.__init__(self, parent, name, type)
        ShuffleboardContainer.__init__(self)

    def buildInto(self, parentTable: NetworkTable, metaTable: NetworkTable) -> None:
        self.buildMetadata(metaTable)
        table = parentTable.getSubTable(self.getTitle())
        table.getEntry(".type").setString("ShuffleboardLayout")
        for component in self.getComponents():
            component.buildInto(table, metaTable.getSubTable(component.getTitle()))
