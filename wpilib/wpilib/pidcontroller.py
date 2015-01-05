#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import threading
import warnings

import hal

from .livewindowsendable import LiveWindowSendable
from .resource import Resource
from ._impl.timertask import TimerTask
from ._impl.utils import match_arglist, HasAttribute

__all__ = ["PIDController"]

class PIDController(LiveWindowSendable):
    """Can be used to control devices via a PID Control Loop.

    Creates a separate thread which reads the given :class:`.PIDSource` and takes
    care of the integral calculations, as well as writing the given
    :class:`.PIDOutput`.
    """
    kDefaultPeriod = .05
    instances = 0

    # Tolerance is the type of tolerance used to specify if the PID controller
    # is on target.  The various implementations of this such as
    # PercentageTolerance and AbsoluteTolerance specify types of tolerance
    # specifications to use.
    def PercentageTolerance_onTarget(self, percentage):
        with self.mutex:
            return (abs(self.getError()) < percentage / 100
                    * (self.maximumInput - self.minimumInput))

    def AbsoluteTolerance_onTarget(self, value):
        with self.mutex:
            return abs(self.getError()) < value

    def __init__(self, *args, **kwargs):
        """Allocate a PID object with the given constants for P, I, D, and F

        Arguments can be structured as follows:

        - Kp, Ki, Kd, Kf, PIDSource, PIDOutput, period
        - Kp, Ki, Kd, PIDSource, PIDOutput, period
        - Kp, Ki, Kd, PIDSource, PIDOutput
        - Kp, Ki, Kd, Kf, PIDSource, PIDOutput

        :param Kp: the proportional coefficient
        :type  Kp: float or int
        :param Ki: the integral coefficient
        :type  Ki: float or int
        :param Kd: the derivative coefficient
        :type  Kd: float or int
        :param Kf: the feed forward term
        :type  Kf: float or int
        :param source: Called to get values
        :type  source: A function, or an object that implements :class:`.PIDSource`
        :param output: Receives the output percentage
        :type  output: A function, or an object that implements :class:`.PIDOutput`
        :param period: the loop time for doing calculations. This particularly
            effects calculations of the integral and differential terms.
            The default is 50ms.
        :type  period: float or int
        """

        p_arg = ("Kp", [float, int])
        i_arg = ("Ki", [float, int])
        d_arg = ("Kd", [float, int])
        f_arg = ("kf", [float, int])
        source_arg = ("source", [HasAttribute("pidGet"), HasAttribute("__call__")])
        output_arg = ("output", [HasAttribute("pidWrite"), HasAttribute("__call__")])
        period_arg = ("period", [float, int])

        templates = [[p_arg, i_arg, d_arg, f_arg, source_arg, output_arg, period_arg],
                     [p_arg, i_arg, d_arg, source_arg, output_arg, period_arg],
                     [p_arg, i_arg, d_arg, source_arg, output_arg],
                     [p_arg, i_arg, d_arg, f_arg, source_arg, output_arg]]

        _, results = match_arglist('PIDController.__init__',
                                   args, kwargs, templates)

        self.P = results.pop("Kp")     # factor for "proportional" control
        self.I = results.pop("Ki")     # factor for "integral" control
        self.D = results.pop("Kd")     # factor for "derivative" control
        self.F = results.pop("Kf", 0.0)# factor for feedforward term
        self.pidOutput = results.pop("output")
        self.pidInput = results.pop("source")
        self.period = results.pop("period", PIDController.kDefaultPeriod)

        self.maximumOutput = 1.0    # |maximum output|
        self.minimumOutput = -1.0   # |minimum output|
        self.maximumInput = 0.0     # maximum input - limit setpoint to this
        self.minimumInput = 0.0     # minimum input - limit setpoint to this
        self.continuous = False     # do the endpoints wrap around? eg. Absolute encoder
        self.enabled = False        #is the pid controller enabled
        self.prevError = 0.0        # the prior sensor input (used to compute velocity)
        self.totalError = 0.0       #the sum of the errors for use in the integral calc
        self.setpoint = 0.0
        self.error = 0.0
        self.result = 0.0

        self.mutex = threading.RLock()

        self.pid_task = TimerTask('PIDTask%d' % PIDController.instances, self.period, self.calculate)
        self.pid_task.start()
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        PIDController.instances += 1
        hal.HALReport(hal.HALUsageReporting.kResourceType_PIDController,
                      PIDController.instances)

    def free(self):
        """Free the PID object"""
        # TODO: is this useful in Python?  Should make TableListener weakref.
        with self.mutex:
            self.pid_task.cancel()
            self.pidInput = None
            self.pidOutput = None

    def calculate(self):
        """Read the input, calculate the output accordingly, and write to the
        output.  This should only be called by the PIDTask and is created
        during initialization."""
        with self.mutex:
            if self.pidInput is None:
                return
            if self.pidOutput is None:
                return
            enabled = self.enabled # take snapshot of these values...
            pidInput = self.pidInput

        if enabled:
            with self.mutex:
                input = pidInput()
                self.error = self.setpoint - input
                if self.continuous:
                    if abs(self.error) > ((self.maximumInput - self.minimumInput) / 2.0):
                        if self.error > 0:
                            self.error = self.error \
                                    - self.maximumInput + self.minimumInput
                        else:
                            self.error = self.error \
                                    + self.maximumInput - self.minimumInput

                if self.I != 0:
                    potentialIGain = (self.totalError + self.error) * self.I
                    if potentialIGain < self.maximumOutput:
                        if potentialIGain > self.minimumOutput:
                            self.totalError += self.error
                        else:
                            self.totalError = self.minimumOutput / self.I
                    else:
                        self.totalError = self.maximumOutput / self.I

                self.result = self.P * self.error + \
                        self.I * self.totalError + \
                        self.D * (self.error - self.prevError) + \
                        self.setpoint * self.F
                self.prevError = self.error

                if self.result > self.maximumOutput:
                    self.result = self.maximumOutput
                elif self.result < self.minimumOutput:
                    self.result = self.minimumOutput
                pidOutput = self.pidOutput
                result = self.result

            pidOutput(result)

    def setPID(self, p, i, d, f=None):
        """Set the PID Controller gain parameters.
        Set the proportional, integral, and differential coefficients.

        :param p: Proportional coefficient
        :param i: Integral coefficient
        :param d: Differential coefficient
        :param f: Feed forward coefficient (optional)
        """
        with self.mutex:
            self.P = p
            self.I = i
            self.D = d
            if f is not None:
                self.F = f

        table = self.getTable()
        if table is not None:
            table.putNumber("p", p)
            table.putNumber("i", i)
            table.putNumber("d", d)
            if f is not None:
                table.putNumber("f", f)

    def getP(self):
        """Get the Proportional coefficient.

        :returns: proportional coefficient
        """
        with self.mutex:
            return self.P

    def getI(self):
        """Get the Integral coefficient

        :returns: integral coefficient
        """
        with self.mutex:
            return self.I

    def getD(self):
        """Get the Differential coefficient.

        :returns: differential coefficient
        """
        with self.mutex:
            return self.D

    def getF(self):
        """Get the Feed forward coefficient.

        :returns: feed forward coefficient
        """
        with self.mutex:
            return self.F

    def get(self):
        """Return the current PID result.
        This is always centered on zero and constrained the the max and min
        outs.

        :returns: the latest calculated output
        """
        with self.mutex:
            return self.result

    def setContinuous(self, continuous=True):
        """Set the PID controller to consider the input to be continuous.
        Rather then using the max and min in as constraints, it considers them
        to be the same point and automatically calculates the shortest route
        to the setpoint.

        :param continuous: Set to True turns on continuous, False turns off
            continuous
        """
        with self.mutex:
            self.continuous = continuous

    def setInputRange(self, minimumInput, maximumInput):
        """Sets the maximum and minimum values expected from the input.
        
        :param minimumInput: the minimum percentage expected from the input
        :param maximumInput: the maximum percentage expected from the output
        """
        with self.mutex:
            if minimumInput > maximumInput:
                raise ValueError("Lower bound is greater than upper bound")
            self.minimumInput = minimumInput
            self.maximumInput = maximumInput
            self.setSetpoint(self.setpoint)

    def setOutputRange(self, minimumOutput, maximumOutput):
        """Sets the minimum and maximum values to write.

        :param minimumOutput: the minimum percentage to write to the output
        :param maximumOutput: the maximum percentage to write to the output
        """
        with self.mutex:
            if minimumOutput > maximumOutput:
                raise ValueError("Lower bound is greater than upper bound")
            self.minimumOutput = minimumOutput
            self.maximumOutput = maximumOutput

    def setSetpoint(self, setpoint):
        """Set the setpoint for the PIDController.

        :param setpoint: the desired setpoint
        """
        with self.mutex:
            if self.maximumInput > self.minimumInput:
                if setpoint > self.maximumInput:
                    newsetpoint = self.maximumInput
                elif setpoint < self.minimumInput:
                    newsetpoint = self.minimumInput
                else:
                    newsetpoint = setpoint
            else:
                newsetpoint = setpoint
            self.setpoint = newsetpoint

        table = self.getTable()
        if table is not None:
            table.putNumber("setpoint", newsetpoint)

    def getSetpoint(self):
        """Returns the current setpoint of the PIDController.

        :returns: the current setpoint
        """
        with self.mutex:
            return self.setpoint

    def getError(self):
        """Returns the current difference of the input from the setpoint.

        :return: the current error
        """
        with self.mutex:
            #return self.error
            return self.getSetpoint() - self.pidInput()

    def setTolerance(self, percent):
        """Set the percentage error which is considered tolerable for use with
        :func:`onTarget`. (Input of 15.0 = 15 percent)

        :param percent: error which is tolerable

        .. deprecated:: 2015.1

            Use :func:`setPercentTolerance` or :func:`setAbsoluteTolerance`
            instead.
        """
        warnings.warn("use setPercentTolerance or setAbsoluteTolerance instead",
                      DeprecationWarning)
        with self.mutex:
            self.onTarget = lambda: \
                    self.PercentageTolerance_onTarget(percent)

    def setAbsoluteTolerance(self, absvalue):
        """Set the absolute error which is considered tolerable for use with
        :func:`onTarget`.

        :param absvalue: absolute error which is tolerable in the units of the
            input object
        """
        with self.mutex:
            self.onTarget = lambda: \
                    self.AbsoluteTolerance_onTarget(absvalue)

    def setPercentTolerance(self, percentage):
        """Set the percentage error which is considered tolerable for use with
        :func:`onTarget`. (Input of 15.0 = 15 percent)

        :param percentage: percent error which is tolerable
        """
        with self.mutex:
            self.onTarget = lambda: \
                    self.PercentageTolerance_onTarget(percentage)

    def onTarget(self):
        """Return True if the error is within the percentage of the total input
        range, determined by setTolerance. This assumes that the maximum and
        minimum input were set using :func:`setInput`.

        :returns: True if the error is less than the tolerance
        """
        raise ValueError("No tolerance value set when using PIDController.onTarget()")

    def enable(self):
        """Begin running the PIDController."""
        with self.mutex:
            self.enabled = True

        table = self.getTable()
        if table is not None:
            table.putBoolean("enabled", True)

    def disable(self):
        """Stop running the PIDController, this sets the output to zero before
        stopping."""
        with self.mutex:
            self.pidOutput(0)
            self.enabled = False

        table = self.getTable()
        if table is not None:
            table.putBoolean("enabled", False)

    def isEnable(self):
        """Return True if PIDController is enabled."""
        with self.mutex:
            return self.enabled

    def reset(self):
        """Reset the previous error, the integral term, and disable the
        controller."""
        with self.mutex:
            self.disable()
            self.prevError = 0
            self.totalError = 0
            self.result = 0

    def getSmartDashboardType(self):
        return "PIDController"

    def valueChanged(self, table, key, value, isNew):
        if key == "p" or key == "i" or key == "d" or key == "f":
            Kp = table.getNumber("p", 0.0)
            Ki = table.getNumber("i", 0.0)
            Kd = table.getNumber("d", 0.0)
            Kf = table.getNumber("f", 0.0)
            if (self.getP() != Kp or self.getI() != Ki or self.getD() != Kd or
                self.getF() != Kf):
                self.setPID(Kp, Ki, Kd, Kf)
        elif key == "setpoint":
            if self.getSetpoint() != float(value):
                self.setSetpoint(float(value))
        elif key == "enabled":
            if self.isEnable() != bool(value):
                if bool(value):
                    self.enable()
                else:
                    self.disable()

    def initTable(self, table):
        oldtable = self.getTable()
        if oldtable is not None:
            oldtable.removeTableListener(self.valueChanged)
        self.table = table
        if table is not None:
            table.putNumber("p", self.getP())
            table.putNumber("i", self.getI())
            table.putNumber("d", self.getD())
            table.putNumber("f", self.getF())
            table.putNumber("setpoint", self.getSetpoint())
            table.putBoolean("enabled", self.isEnable())
            table.addTableListener(self.valueChanged, False)

    def startLiveWindowMode(self):
        self.disable()

    def stopLiveWindowMode(self):
        pass
