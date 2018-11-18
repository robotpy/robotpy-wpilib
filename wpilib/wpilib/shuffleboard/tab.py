# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardTab.java
from .container import ShuffleboardContainer
from .root import ShuffleboardRoot

class ShuffleboardTab(ShuffleboardContainer):
    def __init__(self, root: ShuffleboardRoot, title: str):
        super().__init__()
        self.root = root
        self.title = title

    def getTitle(self):
        return self.title

    def getRoot(self):
        return self.root

    def buildInto(self, parentTable, metaTable) -> None:
        tabTable = parentTable.getSubTable(self.title)
        tabTable.getEntry(".type").setString("ShuffleboardTab")
        for component in self.getComponents():
            component.buildInto(tabTable, metaTable.getSubTable(component.getTitle()))

