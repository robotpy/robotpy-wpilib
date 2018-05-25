# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/SendableBase.java
# ----------------------------------------------------------------------------
# Copyright (c) 2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import threading
import warnings
from .sendable import Sendable
from .livewindow import LiveWindow
from ._impl.utils import match_arglist


__all__ = ["SendableBase"]


class SendableBase(Sendable):
    """
    Base class for all sensors. Stores most recent status information as well as containing utility
    functions for checking channels and error processing.
    """

    def __init__(self, addLiveWindow: bool = True) -> None:
        """
        Creates an instance of the sensor base.
   
        :param addLiveWindow: if true, add this Sendable to LiveWindow
        """
        self.name = ""
        self.subsystem = "Ungrouped"
        self.mutex = threading.RLock()

        if addLiveWindow:
            LiveWindow.add(self)

    def free(self) -> None:
        """
        Free the resources used by this object.

        .. deprecated:: 2019.0.0
            Use close instead 
        """
        warnings.warn("use close instead", DeprecationWarning, stacklevel=2)
        self.close()

    def close(self):
        """
        Free the resources used by this object.
        """
        LiveWindow.remove(self)

    def getName(self) -> str:
        with self.mutex:
            return self.name

    def _setName(self, name: str) -> None:
        with self.mutex:
            self.name = name

    def setName(self, *args, **kwargs) -> None:
        """
        Sets the name of this Sendable object.

        Arguments can be structured as follows:

        - name
        - subsystem, name
        - moduleType, channel
        - moduleType, moduleNumber, channel

        :param name: name
        :type name: str
        :param subsystem: subsystem name
        :type subsystem: str
        :param moduleType: A string that defines the module name in the label for the value
        :type moduleType: str
        :param channel: The channel number the device is plugged into
        :type channel: int
        :param moduleNumber: The number of the particular module type
        :type moduleNumber: int
        """
        name_arg = ("name", [str])
        subsystem_arg = ("subsystem", [str])
        moduleType_arg = ("moduleType", [str])
        channel_arg = ("channel", [int])
        moduleNumber_arg = ("moduleNumber", [int])

        templates = [
            [name_arg],
            [subsystem_arg, name_arg],
            [moduleType_arg, channel_arg],
            [moduleType_arg, moduleNumber_arg, channel_arg],
        ]

        index, results = match_arglist("SendableBase.setName", args, kwargs, templates)

        if index == 0:
            self._setName(results["name"])
        elif index == 1:
            self._setNameAndSubsystem(results["subsystem"], results["name"])
        elif index == 2:
            self._setName("{moduleType}[{channel}]".format_map(results))
        elif index == 3:
            self._setName("{moduleType}[{moduleNumber},{channel}]".format_map(results))

    def getSubsystem(self) -> str:
        with self.mutex:
            return self.subsystem

    def setSubsystem(self, subsystem: str) -> None:
        with self.mutex:
            self.subsystem = subsystem

    def addChild(self, child: object) -> None:
        """
        Add a child component

        :param child: child component
        """
        LiveWindow.addChild(self, child)
