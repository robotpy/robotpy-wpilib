# validated: 2017-09-24 AA e1195e8b9dab edu/wpi/first/wpilibj/PIDOutput.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

__all__ = ["PIDOutput"]


class PIDOutput:
    """This interface allows :class:`.PIDController` to write its results to
    its output.
    """

    def pidWrite(self, output: float) -> None:
        """Set the output to the value calculated by :class:`.PIDController`.

        :param output: the value calculated by PIDController
        """
        raise NotImplementedError
