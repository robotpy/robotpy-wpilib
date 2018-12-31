# validated: 2017-12-27 TW 8b7aa61091df edu/wpi/first/wpilibj/Utility.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

__all__ = ["Utility"]


class Utility:
    """Contains global utility functions

    .. deprecated:: 2018.0.0
        Use :class:`.RobotController` instead
    """

    @staticmethod
    def getFPGAVersion() -> int:
        """Return the FPGA Version number.

        .. deprecated:: 2018.0.0
            Use :meth:`.RobotController.getFPGAVersion` instead

        :returns: FPGA Version number.
        """
        return hal.getFPGAVersion()

    @staticmethod
    def getFPGARevision() -> int:
        """Return the FPGA Revision number. The format of the revision is 3
        numbers.  The 12 most significant bits are the Major Revision. the
        next 8 bits are the Minor Revision. The 12 least significant bits
        are the Build Number.

        .. deprecated:: 2018.0.0
            Use :meth:`.RobotController.getFPGARevision` instead

        :returns: FPGA Revision number.
        """
        return hal.getFPGARevision()

    @staticmethod
    def getFPGATime() -> int:
        """Read the microsecond timer from the FPGA.

        .. deprecated:: 2018.0.0
            Use :meth:`.RobotController.getFPGATime` instead

        :returns: The current time in microseconds according to the FPGA.
        """
        return hal.getFPGATime()

    @staticmethod
    def getUserButton() -> bool:
        """Get the state of the "USER" button on the roboRIO.

        .. deprecated:: 2018.0.0
            Use :meth:`.RobotController.getUserButton` instead

        :returns: True if the button is currently pressed down
        """
        return hal.getFPGAButton()
