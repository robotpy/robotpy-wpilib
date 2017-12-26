# validated: 2017-12-16 EN f9bece2ffbf7 edu/wpi/first/wpilibj/command/PIDSubsystem.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .subsystem import Subsystem

from ..pidcontroller import PIDController

__all__ = ["PIDSubsystem"]

class PIDSubsystem(Subsystem):
    """This class is designed to handle the case where there is a Subsystem
    which uses a single {@link PIDController} almost constantly (for instance,
    an elevator which attempts to stay at a constant height).

    It provides some convenience methods to run an internal PIDController.
    It also allows access to the internal PIDController in order to give total
    control to the programmer.
    """

    def __init__(self, p, i, d, period=None, f=0.0, name=None):
        """Instantiates a PIDSubsystem that will use the given p, i and d
        values.
        It will use the class name as its name unless otherwise specified.
        It will also space the time between PID loop calculations to be equal
        to the given period.
        
        :param p: the proportional value
        :param i: the integral value
        :param d: the derivative value
        :param period: the time (in seconds) between calculations (optional)
        :param f: the feed forward value
        :param name: the name (optional)
        """
        super().__init__(name)
        if period is None:
            period = PIDController.kDefaultPeriod
        self.controller = PIDController(p, i, d, f, self.returnPIDInput,
                                        self.usePIDOutput, period)
        self.addChild(self.controller)

    def getPIDController(self):
        """Returns the PIDController used by this PIDSubsystem.
        Use this if you would like to fine tune the pid loop.

        Notice that calling :meth:`setSetpoint` on the controller
        will not result in the setpoint being trimmed to be in
        the range defined by :meth:`setSetpointRange`.

        :returns: the :class:`.PIDController` used by this PIDSubsystem
        """
        return self.controller

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

    def setInputRange(self, minimumInput, maximumInput):
        """Sets the maximum and minimum values expected from the input.

        :param minimumInput: the minimum value expected from the input
        :param maximumInput: the maximum value expected from the output
        """
        self.controller.setInputRange(minimumInput, maximumInput)

    def setOutputRange(self, minimumOutput, maximumOutput):
        """Sets the maximum and minimum values to write.

        :param minimumOutput: the minimum value to write to the output
        :param maximumOutput: the maximum value to write to the output
        """
        self.controller.setOutputRange(minimumOutput, maximumOutput)

    def setAbsoluteTolerance(self, t):
        """Set the absolute error which is considered tolerable for use with
        OnTarget.
        
        :param t: The absolute tolerance (same range as the PIDInput values)
        """
        self.controller.setAbsoluteTolerance(t)

    def setPercentTolerance(self, p):
        """Set the percentage error which is considered tolerable for use with
        OnTarget.
        
        :param p: The percentage tolerance (value of 15.0 == 15 percent)
        """
        self.controller.setPercentTolerance(p)

    def onTarget(self):
        """Return True if the error is within the percentage of the total
        input range, determined by setAbsoluteTolerance or setPercentTolerance.
        This assumes that the maximum and minimum input were set using
        setInput.
        
        :returns: True if the error is less than the tolerance
        """
        return self.controller.onTarget()

    def returnPIDInput(self):
        """Returns the input for the pid loop.

        It returns the input for the pid loop, so if this command was based
        off of a gyro, then it should return the angle of the gyro

        All subclasses of PIDSubsystem must override this method.

        This method will be called in a different thread then the Scheduler
        thread.

        :returns: the value the pid loop should use as input
        """
        raise NotImplementedError

    def usePIDOutput(self, output):
        """Uses the value that the pid loop calculated.  The calculated value
        is the "output" parameter.
        This method is a good time to set motor values, maybe something along
        the lines of `driveline.tankDrive(output, -output)`.

        All subclasses of PIDSubsystem should override this method.

        This method will be called in a different thread then the Scheduler
        thread.

        :param output: the value the pid loop calculated
        """
        pass

    def enable(self):
        """Enables the internal :class:`.PIDController`
        """
        self.controller.enable()

    def disable(self):
        """Disables the internal :class:`.PIDController`
        """
        self.controller.disable()
