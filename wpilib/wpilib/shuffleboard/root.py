# validated: 2018-11-18 EN 175c6c1f0130 edu/wpi/first/wpilibj/shuffleboard/ShuffleboardRoot.java

class ShuffleboardRoot:
    """
    The root of the data placed in Shuffleboard. It contains the tabs, but no 
    data is placed directly in the root.
    """
    def getTab(self, title: str) -> 'ShuffleboardTab':
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
