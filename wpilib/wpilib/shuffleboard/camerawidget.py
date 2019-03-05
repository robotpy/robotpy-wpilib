# validated: 2019-03-05 DV 80f87ff8ad6e edu/wpi/first/wpilibj/shuffleboard/SendableCameraWrapper.java
# ----------------------------------------------------------------------------
# Copyright (c) 2019 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .container import ShuffleboardContainer
from .widget import ShuffleboardWidget


class CameraWidget(ShuffleboardWidget):
    """A Shuffleboard widget that displays a camera stream from CameraServer.

    Usable via :meth:`.ShuffleboardContainer.addCamera`.
    """

    # python-specific: analogous to SendableCameraWrapper without SendableBase

    __slots__ = ("uri", "not_created")

    kProtocol = "camera_server://"

    def __init__(self, parent: ShuffleboardContainer, title: str, camera_name: str):
        super().__init__(parent, title)
        self.uri = self.kProtocol + camera_name
        self.not_created = True

    def buildInto(self, parentTable, metaTable) -> None:
        self.buildMetadata(metaTable)
        if self.not_created:
            table = parentTable.getSubTable(self.getTitle())
            table.putString(".ShuffleboardURI", self.uri)
            self.not_created = False
