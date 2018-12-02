# validated: 2018-10-30 EN 0b113ad9ce93 edu/wpi/first/wpilibj/command/PIDCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .command import Command

from ..pidcontroller import PIDController

__all__ = ["PIDCommand"]


class PIDCommand(Command):
    """This class defines a Command which interacts heavily with a PID loop.

    It provides some convenience methods to run an internal PIDController.
    It will also start and stop said PIDController when the PIDCommand is
    first initialized and ended/interrupted.
    """

    def __init__(
        self,
        p,
        i,
        d,
        period=PIDController.kDefaultPeriod,
        f=0.0,
        name=None,
        subsystem=None,
    ):
        """Instantiates a PIDCommand that will use the given p, i and d values.
        It will use the class name as its name unless otherwise specified.
        It will also space the time between PID loop calculations to be equal
        to the given period.
        
        :param p: the proportional value
        :param i: the integral value
        :param d: the derivative value
        :param period: the time (in seconds) between calculations (optional)
        :param f: the feed forward value
        :param name: the name (optional)
        :param subsystem: the subsystem that this command requires
        """
        super().__init__(name, subsystem=subsystem)
        self.controller = PIDController(
            p, i, d, f, self.returnPIDInput, self.usePIDOutput, period
        )

    def getPIDController(self):
        """Returns the PIDController used by this PIDCommand.
        Use this if you would like to fine tune the pid loop.

        Notice that calling setSetpoint(...) on the controller
        will not result in the setpoint being trimmed to be in
        the range defined by setSetpointRange(...).

        :returns: the PIDController used by this PIDCommand
        """
        return self.controller

    def _initialize(self):
        self.controller.enable()

    def _end(self):
        self.controller.disable()

    def _interrupted(self):
        self._end()

    def setSetpointRelative(self, deltaSetpoint):
        """Adds the given value to the setpoint.
        If :meth:`setRange` was used, then the bounds will still be honored by
        this method.
        
        :param deltaSetpoint: the change in the setpoint
        """
        self.setSetpoint(self.getSetpoint() + deltaSetpoint)

    def setSetpoint(self, setpoint):
        """Sets the setpoint to the given value.  If :meth:`setRange` was called,
        then the given setpoint will be trimmed to fit within the range.
        
        :param setpoint: the new setpoint
        """
        self.controller.setSetpoint(setpoint)

    def getSetpoint(self):
        """Returns the setpoint.
        
        :returns: the setpoint
        """
        return self.controller.getSetpoint()

    def getPosition(self):
        """Returns the current position
        
        :returns: the current position
        """
        return self.returnPIDInput()

    def returnPIDInput(self):
        """Returns the input for the pid loop.

        It returns the input for the pid loop, so if this command was based
        off of a gyro, then it should return the angle of the gyro

        All subclasses of PIDCommand must override this method.

        This method will be called in a different thread then the :class:`.Scheduler`
        thread.

        :returns: the value the pid loop should use as input
        """
        raise NotImplementedError

    def usePIDOutput(self, output):
        """Uses the value that the pid loop calculated.  The calculated value
        is the "output" parameter.
        This method is a good time to set motor values, maybe something along
        the lines of `driveline.tankDrive(output, -output)`.

        All subclasses of PIDCommand should override this method.

        This method will be called in a different thread then the Scheduler
        thread.

        :param output: the value the pid loop calculated
        """
        pass

    def initSendable(self, builder):
        self.controller.initSendable(builder)
        super().initSendable(builder)
        builder.setSmartDashboardType("PIDCommand")
