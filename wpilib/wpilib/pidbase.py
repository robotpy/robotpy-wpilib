# validated: 2019-02-16 DS 74f7ba04b09c edu/wpi/first/wpilibj/PIDBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2018. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import threading
import warnings

import hal

from .sendablebuilder import SendableBuilder
from .interfaces.pidsource import PIDSource
from .sendablebase import SendableBase
from .resource import Resource
from .timer import Timer
from .lineardigitalfilter import LinearDigitalFilter

__all__ = ["PIDBase"]


class PIDBase(SendableBase):
    """Class implements a PID Control Loop.

    Creates a separate thread which reads the given PIDSource and takes care of the integral
    calculations, as well as writing the given PIDOutput.

    This feedback controller runs in discrete time, so time deltas are not used in the integral
    and derivative calculations. Therefore, the sample rate affects the controller's behavior for a
    given set of PID constants.

    """

    kDefaultPeriod = 0.05
    instances = 0

    PIDSourceType = PIDSource.PIDSourceType

    # Tolerance is the type of tolerance used to specify if the PID controller
    # is on target.  The various implementations of this such as
    # PercentageTolerance and AbsoluteTolerance specify types of tolerance
    # specifications to use.
    def PercentageTolerance_onTarget(self, percentage: float) -> bool:
        return abs(self.getError()) < percentage / 100.0 * self.inputRange

    def AbsoluteTolerance_onTarget(self, value: float) -> bool:
        return abs(self.getError()) < value

    def __init__(self, Kp, Ki, Kd, Kf, source, output):
        """Allocate a PID object with the given constants for P, I, D, and F

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
        """

        super().__init__(False)

        self.P = Kp  # factor for "proportional" control
        self.I = Ki  # factor for "integral" control
        self.D = Kd  # factor for "derivative" control
        self.F = Kf  # factor for feedforward term
        self.pidOutput = output
        self.origSource = source
        self.filter = LinearDigitalFilter.movingAverage(self.origSource, 1)
        self.pidInput = self.filter

        self.pidInput = PIDSource.from_obj_or_callable(self.pidInput)

        if hasattr(self.pidOutput, "pidWrite"):
            self.pidOutput = self.pidOutput.pidWrite

        # fmt: off
        self.maximumOutput = 1.0    # |maximum output|
        self.minimumOutput = -1.0   # |minimum output|
        self.maximumInput = 0.0     # maximum input - limit setpoint to this
        self.minimumInput = 0.0     # minimum input - limit setpoint to this
        self.inputRange = 0.0       # input range - difference between maximum and minimum
        self.continuous = False     # do the endpoints wrap around? eg. Absolute encoder
        self.enabled = False        # is the pid controller enabled
        self.prevError = 0.0        # the prior error (used to compute velocity)
        self.totalError = 0.0       #the sum of the errors for use in the integral calc
        self.setpoint = 0.0
        self.prevSetpoint = 0.0
        self.error = 0.0
        self.result = 0.0
        # fmt: on

        self.mutex = threading.RLock()
        self.pidWriteMutex = threading.RLock()

        self.setpointTimer = Timer()
        self.setpointTimer.start()

        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        PIDBase.instances += 1
        hal.report(hal.UsageReporting.kResourceType_PIDController, PIDBase.instances)
        self.setName("PIDController", PIDBase.instances)

    def _calculate(self) -> None:
        """Read the input, calculate the output accordingly, and write to the
        output.  This should only be called by the PIDTask and is created
        during initialization."""
        if self.origSource is None or self.pidOutput is None:
            return

        with self.mutex:
            enabled = self.enabled  # take snapshot of these values...

        if enabled:
            feedForward = self.calculateFeedForward()

            with self.mutex:
                input = self.pidInput.pidGet()
                pidSourceType = self.pidInput.getPIDSourceType()
                P = self.P
                I = self.I
                D = self.D
                minimumOutput = self.minimumOutput
                maximumOutput = self.maximumOutput
                prevError = self.prevError
                error = self.getContinuousError(self.setpoint - input)
                totalError = self.totalError

            # start

            if pidSourceType == self.PIDSourceType.kRate:
                if P != 0:
                    totalError = self.clamp(
                        totalError + error, minimumOutput / P, maximumOutput / P
                    )

                result = P * totalError + D * error + feedForward

            else:
                if I != 0:
                    totalError = self.clamp(
                        totalError + error, minimumOutput / I, maximumOutput / I
                    )

                result = (
                    P * error + I * totalError + D * (error - prevError) + feedForward
                )

            result = self.clamp(result, minimumOutput, maximumOutput)

            with self.pidWriteMutex:
                with self.mutex:
                    enabled = self.enabled
                if enabled:
                    self.pidOutput(result)

            with self.mutex:
                self.prevError = error
                self.error = error
                self.totalError = totalError
                self.result = result

    def calculateFeedForward(self) -> float:
        """Calculate the feed forward term

        Both of the provided feed forward calculations are velocity feed forwards.
        If a different feed forward calculation is desired, the user can override
        this function and provide his or her own. This function  does no
        synchronization because the PIDController class only calls it in
        synchronized code, so be careful if calling it oneself.

        If a velocity PID controller is being used, the F term should be set to 1
        over the maximum setpoint for the output. If a position PID controller is
        being used, the F term should be set to 1 over the maximum speed for the
        output measured in setpoint units per this controller's update period (see
        the default period in this class's constructor).
        """
        if self.pidInput.getPIDSourceType() == self.PIDSourceType.kRate:
            return self.F * self.getSetpoint()
        else:
            temp = self.F * self.getDeltaSetpoint()
            self.prevSetpoint = self.setpoint
            self.setpointTimer.reset()
            return temp

    def setPID(self, p: float, i: float, d: float, f: float = 0.0) -> None:
        """Set the PID Controller gain parameters.
        Set the proportional, integral, and differential coefficients.

        :param p: Proportional coefficient
        :param i: Integral coefficient
        :param d: Differential coefficient
        :param f: Feed forward coefficient (optional, default is 0.0)
        """
        with self.mutex:
            self.P = p
            self.I = i
            self.D = d
            self.F = f

    def setP(self, p) -> None:
        """
        Set the Proportional coefficient of the PID controller gain.

        :param p: Proportional coefficient
        """
        with self.mutex:
            self.P = p

    def setI(self, i) -> None:
        """
        Set the Integral coefficient of the PID controller gain.

        :param i: Integral coefficient
        """
        with self.mutex:
            self.I = i

    def setD(self, d) -> None:
        """
        Set the Differential coefficient of the PID controller gain.

        :param d: differential coefficient
        """
        with self.mutex:
            self.D = d

    def setF(self, f) -> None:
        """
        Set the Feed forward coefficient of the PID controller gain.

        :param f: feed forward coefficient
        """
        with self.mutex:
            self.F = f

    def getP(self) -> float:
        """Get the Proportional coefficient.

        :returns: proportional coefficient
        """
        with self.mutex:
            return self.P

    def getI(self) -> float:
        """Get the Integral coefficient

        :returns: integral coefficient
        """
        with self.mutex:
            return self.I

    def getD(self) -> float:
        """Get the Differential coefficient.

        :returns: differential coefficient
        """
        with self.mutex:
            return self.D

    def getF(self) -> float:
        """Get the Feed forward coefficient.

        :returns: feed forward coefficient
        """
        with self.mutex:
            return self.F

    def get(self) -> float:
        """Return the current PID result.
        This is always centered on zero and constrained the the max and min
        outs.

        :returns: the latest calculated output
        """
        with self.mutex:
            return self.result

    def setContinuous(self, continuous: bool = True) -> None:
        """Set the PID controller to consider the input to be continuous.
        Rather then using the max and min input range as constraints, it considers them
        to be the same point and automatically calculates the shortest route
        to the setpoint.

        :param continuous: Set to True turns on continuous, False turns off
            continuous
        """
        if continuous and self.inputRange <= 0:
            raise ValueError("No input range set when calling setContinuous().")
        with self.mutex:
            self.continuous = continuous

    def setInputRange(self, minimumInput: float, maximumInput: float) -> None:
        """Sets the maximum and minimum values expected from the input.

        :param minimumInput: the minimum percentage expected from the input
        :param maximumInput: the maximum percentage expected from the output
        """
        with self.mutex:
            if minimumInput > maximumInput:
                raise ValueError("Lower bound is greater than upper bound")
            self.minimumInput = minimumInput
            self.maximumInput = maximumInput
            self.inputRange = self.maximumInput - self.minimumInput
            self.setSetpoint(self.setpoint)

    def setOutputRange(self, minimumOutput: float, maximumOutput: float) -> None:
        """Sets the minimum and maximum values to write.

        :param minimumOutput: the minimum percentage to write to the output
        :param maximumOutput: the maximum percentage to write to the output
        """
        with self.mutex:
            if minimumOutput > maximumOutput:
                raise ValueError("Lower bound is greater than upper bound")
            self.minimumOutput = minimumOutput
            self.maximumOutput = maximumOutput

    def setSetpoint(self, setpoint: float) -> None:
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

    def getSetpoint(self) -> float:
        """Returns the current setpoint of the PIDController.

        :returns: the current setpoint
        """
        with self.mutex:
            return self.setpoint

    def getDeltaSetpoint(self) -> float:
        """Returns the change in setpoint over time of the PIDController

        :returns: the change in setpoint over time
        """
        with self.mutex:
            t = self.setpointTimer.get()
            # During testing/simulation it is possible to get a divide by zero because
            # the threads' calls aren't strictly aligned with the master clock.
            if t:
                return (self.setpoint - self.prevSetpoint) / t
            else:
                return 0.0

    def getError(self) -> float:
        """Returns the current difference of the input from the setpoint.

        :return: the current error
        """
        with self.mutex:
            return self.getContinuousError(self.getSetpoint() - self.pidInput.pidGet())

    def getAvgError(self) -> float:
        """
        Returns the current difference of the error over the past few iterations. You can specify the
        number of iterations to average with setToleranceBuffer() (defaults to 1). getAvgError() is
        used for the onTarget() function.

        .. deprecated :: 2018.0.0
            Use getError(), which is now already filtered.

        :returns: the current average of the error
        """
        warnings.warn("use getRate instead", DeprecationWarning)
        with self.mutex:
            return self.getError()

    def setPIDSourceType(self, pidSourceType: PIDSourceType) -> None:
        """Sets what type of input the PID controller will use

        :param pidSourceType: the type of input
        """
        self.pidInput.setPIDSourceType(pidSourceType)

    def getPIDSourceType(self) -> PIDSourceType:
        """Returns the type of input the PID controller is using

        :returns: the PID controller input type
        """
        return self.pidInput.getPIDSourceType()

    def setAbsoluteTolerance(self, absvalue: float) -> None:
        """Set the absolute error which is considered tolerable for use with
        :func:`onTarget`.

        :param absvalue: absolute error which is tolerable in the units of the
            input object
        """
        with self.mutex:
            self.onTarget = lambda: self.AbsoluteTolerance_onTarget(absvalue)

    def setPercentTolerance(self, percentage: float) -> None:
        """Set the percentage error which is considered tolerable for use with
        :func:`onTarget`. (Input of 15.0 = 15 percent)

        :param percentage: percent error which is tolerable
        """
        with self.mutex:
            self.onTarget = lambda: self.PercentageTolerance_onTarget(percentage)

    def setToleranceBuffer(self, bufLength: int) -> None:
        """Set the number of previous error samples to average for tolerancing. When
        determining whether a mechanism is on target, the user may want to use a
        rolling average of previous measurements instead of a precise position or
        velocity. This is useful for noisy sensors which return a few erroneous
        measurements when the mechanism is on target. However, the mechanism will
        not register as on target for at least the specified bufLength cycles.

        :param bufLength: Number of previous cycles to average.
        :type bufLength: int

        .. deprecated:: 2018.0.0
            Use a LinearDigitalFilter as the input
        """
        with self.mutex:
            self.filter = LinearDigitalFilter.movingAverage(self.origSource, bufLength)
            self.pidInput = self.filter

    def onTarget(self) -> bool:
        """Return True if the error is within the percentage of the total input
        range, determined by setTolerance. This assumes that the maximum and
        minimum input were set using :func:`setInput`.

        :returns: True if the error is less than the tolerance
        """
        with self.mutex:
            # python-specific: this is equivalent to the NullTolerance object in Java
            raise ValueError("No tolerance value set when calling onTarget().")

    def reset(self) -> None:
        """Reset the previous error, the integral term, and disable the controller.

        """
        with self.mutex:
            self.prevError = 0
            self.totalError = 0
            self.result = 0

    def pidWrite(self, output: float) -> None:
        """Passes the output directly to setSetpoint().

        PIDControllers can be nested by passing a PIDController as another PIDController's output.
        In that case, the output of the parent controller becomes the input (i.e., the reference) of
        the child.

        It is the caller's responsibility to put the data into a valid form for setSetpoint().

        """
        self.setSetpoint(output)

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("PIDController")
        builder.setSafeState(self.reset)
        builder.addDoubleProperty("p", self.getP, self.setP)
        builder.addDoubleProperty("i", self.getI, self.setI)
        builder.addDoubleProperty("d", self.getD, self.setD)
        builder.addDoubleProperty("f", self.getF, self.setF)
        builder.addDoubleProperty("setpoint", self.getSetpoint, self.setSetpoint)

    def getContinuousError(self, error: float) -> float:
        """
        Wraps error around for continuous inputs. The original error is
        returned if continuous mode is disabled. This is an unsynchronized
        function.

        :param error: The current error of the PID controller.
        :return: Error for continuous inputs.
        """
        if self.continuous and self.inputRange > 0:
            error %= self.inputRange
            if abs(error) > self.inputRange / 2:
                if error > 0:
                    return error - self.inputRange
                else:
                    return error + self.inputRange
        return error

    def clamp(self, value: float, low: float, high: float) -> float:
        return max(low, min(value, high))
