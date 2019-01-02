# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardWidget.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .component import ShuffleboardComponent
from .container import ShuffleboardContainer


class ShuffleboardWidget(ShuffleboardComponent):
    """
    Abstract superclass for widgets.
    """

    def __init__(self, parent: ShuffleboardContainer, title: str):
        super().__init__(parent, title)

    def withWidget(self, widgetType) -> "ShuffleboardWidget":
        """
        Sets the type of widget used to display the data. If not set, the 
        default widget type will be used.

        :param widgetType: the type of the widget used to display the data
        :returns: this widget object
        """
        self.setType(widgetType)
        return self
