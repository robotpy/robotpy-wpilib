# validated: 2019-01-02 EN 59700882f1b1 edu/wpi/first/wpilibj/PIDController.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import warnings

from .sendablebuilder import SendableBuilder

from .interfaces.pidsource import PIDSource
from .lineardigitalfilter import LinearDigitalFilter
from .pidbase import PIDBase
from .notifier import Notifier
from ._impl.utils import match_arglist, HasAttribute

__all__ = ["PIDController"]


class PIDController(PIDBase):
    """Can be used to control devices via a PID Control Loop.

    Creates a separate thread which reads the given :class:`.PIDSource` and takes
    care of the integral calculations, as well as writing the given
    :class:`.PIDOutput`.

    This feedback controller runs in discrete time, so time deltas are not used
    in the integral and derivative calculations. Therefore, the sample rate affects
    the controller's behavior for a given set of PID constants.
    """

    def __init__(self, Kp, Ki, Kd, *args, **kwargs):
        """Allocate a PID object with the given constants for P, I, D, and F

        Arguments can be structured as follows:

        - Kp, Ki, Kd, Kf, source, output, period
        - Kp, Ki, Kd, source, output, period
        - Kp, Ki, Kd, source, output
        - Kp, Ki, Kd, Kf, source, output

        :param Kp: the proportional coefficient
        :param Ki: the integral coefficient
        :param Kd: the derivative coefficient
        :param Kf: the feed forward term
        :param source: Called to get values
        :param output: Receives the output percentage
        :param period: the loop time for doing calculations. This particularly
            effects calculations of the integral and differential terms.
            The default is 0.05 (50ms).
        """
        f_arg = ("Kf", [float, int])
        source_arg = ("source", [HasAttribute("pidGet"), HasAttribute("__call__")])
        output_arg = ("output", [HasAttribute("pidWrite"), HasAttribute("__call__")])
        period_arg = ("period", [float, int])

        templates = [
            [f_arg, source_arg, output_arg, period_arg],
            [source_arg, output_arg, period_arg],
            [source_arg, output_arg],
            [f_arg, source_arg, output_arg],
        ]

        _, results = match_arglist("PIDController.__init__", args, kwargs, templates)

        Kf = results.pop("Kf", 0.0)  # factor for feedforward term
        output = results.pop("output")
        source = results.pop("source")
        super().__init__(Kp, Ki, Kd, Kf, source, output)

        self.period = results.pop("period", self.kDefaultPeriod)

        self.controlLoop = Notifier(self._calculate)
        self.controlLoop.startPeriodic(self.period)

    def close(self) -> None:
        """Free the PID object"""
        super().close()
        # TODO: is this useful in Python?  Should make TableListener weakref.
        if self.controlLoop is not None:
            self.controlLoop.close()
        with self.mutex:
            self.pidInput = None
            self.pidOutput = None
            self.controlLoop = None

    def enable(self) -> None:
        """Begin running the PIDController."""
        with self.mutex:
            self.enabled = True

    def disable(self) -> None:
        """Stop running the PIDController, this sets the output to zero before
        stopping."""
        with self.pidWriteMutex:
            with self.mutex:
                self.enabled = False
            self.pidOutput(0)

    def setEnabled(self, enable: bool) -> None:
        """Set the enabled state of the PIDController."""
        if enable:
            self.enable()
        else:
            self.disable()

    def isEnabled(self) -> bool:
        """Return True if PIDController is enabled."""
        with self.mutex:
            return self.enabled

    def reset(self) -> None:
        """Reset the previous error, the integral term, and disable the
        controller."""
        self.disable()
        super().reset()

    def initSendable(self, builder: SendableBuilder) -> None:
        super().initSendable(builder)
        builder.addBooleanProperty("enabled", self.isEnabled, self.setEnabled)
