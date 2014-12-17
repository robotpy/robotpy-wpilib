#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

__all__ = ["Utility"]

class Utility:
    """Contains global utility functions"""

    @staticmethod
    def getFPGAVersion():
        """Return the FPGA Version number.

        :returns: FPGA Version number.
        :rtype: int
        """
        return hal.getFPGAVersion()

    @staticmethod
    def getFPGARevision():
        """Return the FPGA Revision number. The format of the revision is 3
        numbers.  The 12 most significant bits are the Major Revision. the
        next 8 bits are the Minor Revision. The 12 least significant bits
        are the Build Number.

        :returns: FPGA Revision number.
        :rtype: int
        """
        return hal.getFPGARevision()

    @staticmethod
    def getFPGATime():
        """Read the microsecond timer from the FPGA.

        :returns: The current time in microseconds according to the FPGA.
        :rtype: int
        """
        return hal.getFPGATime()

    @staticmethod
    def getUserButton():
        """Get the state of the "USER" button on the RoboRIO.

        :returns: True if the button is currently pressed down
        :rtype: bool
        """
        return hal.getFPGAButton()
