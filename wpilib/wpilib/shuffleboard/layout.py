# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardLayout.java

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
