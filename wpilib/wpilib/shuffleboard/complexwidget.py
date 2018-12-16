# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ComplexWidget.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from ..sendablebuilder import SendableBuilder
from ..sendable import Sendable
from .widget import ShuffleboardWidget
from .container import ShuffleboardContainer


class ComplexWidget(ShuffleboardWidget):
    def __init__(self, parent: ShuffleboardContainer, title: str, sendable: Sendable):
        super().__init__(parent, title)
        self.sendable = sendable
        self.builder = None

    def buildInto(self, parentTable, metaTable) -> None:
        self.buildMetadata(metaTable)
        if self.builder is None:
            self.builder = SendableBuilder()
            self.builder.setTable(parentTable.getSubTable(self.getTitle()))
            self.sendable.initSendable(self.builder)
            self.builder.startListeners()

        self.builder.updateTable()

    def enableIfActuator(self):
        """
        Enables user control of this widget in the Shuffleboard application. 
        Has no effect if the sendable is not marked as an actuator 
        with :meth:`.SendableBuilder.setActuator`.
        """
        if self.builder.isActuator():
            self.builder.startLiveWindowMode()

    def disableIfActuator(self):
        """
        Disables user control of this widget in the Shuffleboard application. 
        Has no effect if the sendable is not marked as an actuator 
        with :meth:`.SendableBuilder.setActuator`.
        """
        if self.builder.isActuator():
            self.builder.stopLiveWindowMode()
