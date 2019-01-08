# validated: 2019-01-05 TW 01d13220660c edu/wpi/first/wpilibj/shuffleboard/ShuffleboardTab.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .container import ShuffleboardContainer
from .root import ShuffleboardRoot


class ShuffleboardTab(ShuffleboardContainer):
    def __init__(self, root: ShuffleboardRoot, title: str):
        super().__init__()
        self.root = root
        self.title = title

    def getTitle(self) -> str:
        return self.title

    def getRoot(self) -> ShuffleboardRoot:
        return self.root

    def buildInto(self, parentTable, metaTable) -> None:
        tabTable = parentTable.getSubTable(self.title)
        tabTable.getEntry(".type").setString("ShuffleboardTab")
        for component in self.getComponents():
            component.buildInto(tabTable, metaTable.getSubTable(component.getTitle()))
