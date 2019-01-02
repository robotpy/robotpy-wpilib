# validated: 2018-12-15 EN 6f0c185a05c9 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardRoot.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tab import ShuffleboardTab


class ShuffleboardRoot:
    """
    The root of the data placed in Shuffleboard. It contains the tabs, but no 
    data is placed directly in the root.
    """

    def getTab(self, title: str) -> "ShuffleboardTab":
        """
        Gets the tab with the given title, creating it if it does not 
        already exist.

        :param title: the title of the tab
        :returns: the tab with the given title
        """
        raise NotImplementedError

    def update(self) -> None:
        """Updates all tabs."""
        raise NotImplementedError

    def enableActuatorWidgets(self) -> None:
        """Enables all widgets in Shuffleboard that offer user control over actuators."""
        raise NotImplementedError

    def disableActuatorWidgets(self) -> None:
        """Disables all widgets in Shuffleboard that offer user control over actuators."""
        raise NotImplementedError

    def selectTab(self, index_or_title) -> None:
        """
        Selects the tab in the dashboard with the given index in the 
        range [0..n-1], where `n` is the number of tabs in the dashboard at 
        the time this method is called.

        Or

        Selects the tab in the dashboard with the given title.

        :param index_or_title: when integer, the index of the tab to select.
                               when string, the title of the tab to select.
        """
        raise NotImplementedError
