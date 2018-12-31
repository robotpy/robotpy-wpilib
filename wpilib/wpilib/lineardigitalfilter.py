# validated: 2018-09-30 EN a11fcb605d15 edu/wpi/first/wpilibj/filters/LinearDigitalFilter.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import collections
import math
from operator import mul
from typing import Sequence

import hal

from .interfaces.pidsource import PIDSource
from .filter import Filter

__all__ = ["LinearDigitalFilter"]


class LinearDigitalFilter(Filter):
    """This class implements a linear, digital filter. All types of FIR and IIR
    filters are supported. Static factory methods are provided to create commonly
    used types of filters.
    
    Filters are of the form::
    
        y[n] = (b0*x[n] + b1*x[n-1] + ... + bP*x[n-P]) - (a0*y[n-1] + a2*y[n-2] + ... + aQ*y[n-Q])
    
    Where:
    
    * ``y[n]`` is the output at time "n"
    * ``x[n]`` is the input at time "n"
    * ``y[n-1]`` is the output from the LAST time step ("n-1")
    * ``x[n-1]`` is the input from the LAST time step ("n-1")
    * ``b0...bP`` are the "feedforward" (FIR) gains
    * ``a0...aQ`` are the "feedback" (IIR) gains
    
    .. note:: IMPORTANT! Note the "-" sign in front of the feedback term! This is a common
              convention in signal processing.
    
    What can linear filters do? Basically, they can filter, or diminish, the
    effects of undesirable input frequencies. High frequencies, or rapid changes,
    can be indicative of sensor noise or be otherwise undesirable. A "low pass"
    filter smoothes out the signal, reducing the impact of these high frequency
    components.  Likewise, a "high pass" filter gets rid of slow-moving signal
    components, letting you detect large changes more easily.
    
    Example FRC applications of filters:
    
    * Getting rid of noise from an analog sensor input (note: the roboRIO's FPGA
      can do this faster in hardware)
    * Smoothing out joystick input to prevent the wheels from slipping or the
      robot from tipping
    * Smoothing motor commands so that unnecessary strain isn't put on
      electrical or mechanical components
    * If you use clever gains, you can make a PID controller out of this class!
    
    For more on filters, I highly recommend the following articles:
    
    * http://en.wikipedia.org/wiki/Linear_filter
    * http://en.wikipedia.org/wiki/Iir_filter
    * http://en.wikipedia.org/wiki/Fir_filter
    
    .. note:: :meth:`pidGet` should be called by the user on a known, regular period.
        You can set up a Notifier to do this (look at the :class:`.PIDController`
        class), or do it "inline" with code in a periodic function.
    
    .. note:: For ALL filters, gains are necessarily a function of frequency. If
        you make a filter that works well for you at, say, 100Hz, you will most
        definitely need to adjust the gains if you then want to run it at 200Hz!
        Combining this with Note 1 - the impetus is on YOU as a developer to make
        sure :meth:`pidGet` gets called at the desired, constant frequency!
        
    There are static methods you can use to build common filters:
    
    * :meth:`highPass`
    * :meth:`movingAverage`
    * :meth:`singlePoleIIR`
    
    """

    instances = 0

    def __init__(
        self, source: PIDSource, ffGains: Sequence[float], fbGains: Sequence[float]
    ) -> None:
        """Constructor. Create a linear FIR or IIR filter
        
        :param source: The PIDSource object that is used to get values
        :param ffGains: The "feed forward" or FIR gains
        :param fbGains: The "feed back" or IIR gains
        """

        super().__init__(source)

        lf = len(ffGains)
        lb = len(fbGains)

        self.inputs = collections.deque([0.0] * lf, maxlen=lf)
        self.outputs = collections.deque([0.0] * lb, maxlen=lb)
        self.inputGains = ffGains.copy()
        self.outputGains = fbGains.copy()

        LinearDigitalFilter.instances += 1
        hal.report(
            hal.UsageReporting.kResourceType_LinearFilter, LinearDigitalFilter.instances
        )

    @staticmethod
    def singlePoleIIR(
        source: PIDSource, timeConstant: float, period: float
    ) -> "LinearDigitalFilter":
        """Creates a one-pole IIR low-pass filter of the form::
        
            y[n] = (1-gain)*x[n] + gain*y[n-1]
            
        Where ``gain = e^(-dt / T)``, ``T`` is the time constant in seconds
        
        This filter is stable for time constants greater than zero
        
        :param source: The PIDSource object that is used to get values
        :param timeConstant: The discrete-time time constant in seconds
        :param period: The period in seconds between samples taken by the user

        :returns: :class:`LinearDigitalFilter`
        """

        gain = math.exp(-period / float(timeConstant))
        ffGains = [1.0 - gain]
        fbGains = [-gain]

        return LinearDigitalFilter(source, ffGains, fbGains)

    @staticmethod
    def highPass(
        source: PIDSource, timeConstant: float, period: float
    ) -> "LinearDigitalFilter":
        """Creates a first-order high-pass filter of the form::
        
            y[n] = gain*x[n] + (-gain)*x[n-1] + gain*y[n-1]
            
        where ``gain = e^(-dt / T)``, ``T`` is the time constant in seconds
        
        This filter is stable for time constants greater than zero
        
        :param source: The PIDSource object that is used to get values
        :param timeConstant: The discrete-time time constant in seconds
        :param period: The period in seconds between samples taken by the user

        :returns: :class:`LinearDigitalFilter`
        """
        gain = math.exp(-period / float(timeConstant))
        ffGains = [gain, -gain]
        fbGains = [-gain]

        return LinearDigitalFilter(source, ffGains, fbGains)

    @staticmethod
    def movingAverage(source: PIDSource, taps: int) -> "LinearDigitalFilter":
        """Creates a K-tap FIR moving average filter of the form::
        
            y[n] = 1/k * (x[k] + x[k-1] + ... + x[0])
        
        This filter is always stable.
        
        :param source: The PIDSource object that is used to get values
        :param taps: The number of samples to average over. Higher = smoother but slower

        :raises: :exc:`ValueError` if number of taps is less than 1
        
        :returns: :class:`LinearDigitalFilter`
        """
        if taps <= 0:
            raise ValueError("Number of taps was not at least 1")

        ffGains = [1.0 / taps] * taps
        fbGains = []

        return LinearDigitalFilter(source, ffGains, fbGains)

    def get(self) -> float:
        """Returns the current filter estimate without also inserting new data as
        :meth:`pidGet` would do.
        
        :returns: The current filter estimate
        """

        # Calculate the new value
        retVal = sum(map(mul, self.inputs, self.inputGains)) - sum(
            map(mul, self.outputs, self.outputGains)
        )

        return retVal

    def reset(self) -> None:
        """Reset the filter state"""
        self.inputs.clear()
        self.outputs.clear()

    def pidGet(self) -> float:
        """Calculates the next value of the filter
        
        :returns: The filtered value at this step
        """

        # Rotate the inputs
        self.inputs.appendleft(self.pidGetSource())

        # Calculate the new value
        retVal = sum(map(mul, self.inputs, self.inputGains)) - sum(
            map(mul, self.outputs, self.outputGains)
        )

        # Rotate the outputs
        self.outputs.appendleft(retVal)

        return retVal
