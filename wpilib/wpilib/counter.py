#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import warnings
import weakref

from .interfaces.counterbase import CounterBase
from .interfaces.pidsource import PIDSource
from .analogtriggeroutput import AnalogTriggerOutput
from .digitalinput import DigitalInput
from .livewindow import LiveWindow
from .sensorbase import SensorBase

__all__ = ["Counter"]

def _freeCounter(counter):
    hal.setCounterUpdateWhenEmpty(counter, True)
    hal.clearCounterUpSource(counter)
    hal.clearCounterDownSource(counter)
    hal.freeCounter(counter)

class Counter(SensorBase):
    """Class for counting the number of ticks on a digital input channel. This
    is a general purpose class for counting repetitive events. It can return
    the number of counts, the period of the most recent cycle, and detect when
    the signal being counted has stopped by supplying a maximum cycle time.

    All counters will immediately start counting - reset() them if you need
    them to be zeroed before use.
    """

    class Mode:
        """Mode determines how and what the counter counts"""
        
        #: two pulse mode
        kTwoPulse = 0
        
        #: semi period mode
        kSemiperiod = 1
        
        #: pulse length mode
        kPulseLength = 2
        
        #: external direction mode
        kExternalDirection = 3

    EncodingType = CounterBase.EncodingType
    PIDSourceParameter = PIDSource.PIDSourceParameter

    def __init__(self, *args, **kwargs):
        """Counter constructor.

        The counter will start counting immediately.

        Positional arguments may be either channel numbers, :class:`.DigitalSource`
        sources, or :class:`.AnalogTrigger` sources in the following order:
        
        - (none)
        - upSource
        - upChannel
        - analogTrigger
        - upSource/upChannel, downSource/downChannel

        For positional arguments, if the passed object has a
        `getChannelForRouting` function, it is assumed to be a DigitalSource.
        If the passed object has a `createOutput` function, it is assumed to
        be an AnalogTrigger.

        Alternatively, sources and/or channels may be passed as keyword
        arguments.  The behavior of specifying both a source and a number
        for the same channel is undefined, as is passing both a positional
        and a keyword argument for the same channel.

        In addition, keyword parameters may be provided for mode, inverted,
        and inputType.

        :param upSource: The source that should be used for up counting.
        :param downSource: The source that should be used for down counting
                           or direction control.
        :param upChannel: The digital input index that should be used for up
                          counting.
        :param downChannel: The digital input index that should be used for
                            down counting or direction control.
        :param analogTrigger: An analog trigger for up counting (assumed to
                              be of kState type; use :func:`setUpSource`
                              for other options).
        :param mode:
            How and what the counter counts (see :class:`.Mode`).  Defaults to
            `Mode.kTwoPulse` for zero or one positional arguments, and
            `Mode.kExternalDirection` for two positional arguments.
        :param inverted:
            Flips the direction of counting.  Defaults to False if unspecified.
            Only used when two sources are specified.
        :param encodingType:
            Either k1X or k2X to indicate 1X or 2X decoding. 4X decoding
            is not supported by Counter; use `Encoder` instead.  Defaults
            to k1X if unspecified.  Only used when two sources are specified.
        """
        # keyword arguments
        upSource = kwargs.pop("aSource", None)
        downSource = kwargs.pop("bSource", None)
        upChannel = kwargs.pop("aChannel", None)
        downChannel = kwargs.pop("bChannel", None)
        analogTrigger = kwargs.pop("analogTrigger", None)
        mode = kwargs.pop("mode", None)
        inverse = kwargs.pop("inverse", False)
        encodingType = kwargs.pop("encodingType", None)

        if kwargs:
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

        # positional arguments
        if len(args) == 0:
            if mode is None:
                mode = self.Mode.kTwoPulse
        elif len(args) == 1:
            if mode is None:
                mode = self.Mode.kTwoPulse
            up = args[0]
            if hasattr(up, "getChannelForRouting"):
                upSource = up
            elif hasattr(up, "createOutput"):
                analogTrigger = up
            else:
                upChannel = up
        elif len(args) == 2:
            if mode is None:
                mode = self.Mode.kExternalDirection
            up, down = args
            if hasattr(up, "getChannelForRouting"):
                upSource = up
            else:
                upChannel = up
            if hasattr(down, "getChannelForRouting"):
                downSource = down
            else:
                downChannel = down
        else:
            raise ValueError("don't know how to handle %d positional arguments" % len(args))

        # convert channels into sources
        if upSource is None:
            if upChannel is not None:
                upSource = DigitalInput(upChannel)
            elif analogTrigger is not None:
                upSource = analogTrigger.createOutput(
                        AnalogTriggerOutput.AnalogTriggerType.STATE)
            else:
                raise ValueError("didn't specify up source")
        if downSource is None:
            if downChannel is None:
                raise ValueError("didn't specify down source")
            downSource = DigitalInput(downChannel)

        # save to instance variables
        self.upSource = upSource
        self.downSource = downSource
        self.distancePerPulse = 1.0 # distance of travel for each tick
        self.pidSource = PIDSourceParameter.kDistance

        # create counter
        self._counter, self.index = hal.initializeCounter(mode)
        self._counter_finalizer = \
                weakref.finalize(self, _freeCounter, self._counter)

        hal.HALReport(hal.HALUsageReporting.kResourceType_Counter, self.index,
                      mode)

        # set sources on counter
        if upSource is not None:
            hal.setCounterUpSource(self._counter,
                                   upSource.getChannelForRouting(),
                                   upSource.getAnalogTriggerForRouting())
        if downSource is not None:
            hal.setCounterDownSource(self.counter,
                                     downSource.getChannelForRouting(),
                                     downSource.getAnalogTriggerForRouting())

        # when given two sources, set edges
        if upSource is not None and downSource is not None:
            if encodingType == self.EncodingType.k1X:
                self.setUpSourceEdge(True, False)
            else:
                self.setUpSourceEdge(True, True)
            self.setDownSourceEdge(inverse, True)

    @property
    def counter(self):
        if not self._counter_finalizer.alive:
            return None
        return self._counter

    def free(self):
        self._counter_finalizer()

    def setUpSource(self, *args, **kwargs):
        """Set the upsource for the counter.

        This function accepts either a digital channel index, a
        `DigitalSource`, or an `AnalogTrigger` as positional arguments:
        
        - source
        - channel
        - analogTrigger, triggerType

        For positional arguments, if the passed object has a
        `getChannelForRouting` function, it is assumed to be a DigitalSource.
        If the passed object has a `createOutput` function, it is assumed to
        be an AnalogTrigger.

        Alternatively, sources and/or channels may be passed as keyword
        arguments.  The behavior of specifying both a source and a number
        for the same channel is undefined, as is passing both a positional
        and a keyword argument for the same channel.

        :param channel: the digital port to count
        :param source: the digital source to count
        :param analogTrigger:
            The :class:`.AnalogTrigger` object that is used for the Up Source
        :param triggerType:
            The :class:`.AnalogTrigger` output that will trigger the counter.
            Defaults to kState if not specified.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")

        # keyword arguments
        source = kwargs.pop("source", None)
        channel = kwargs.pop("channel", None)
        analogTrigger = kwargs.pop("analogTrigger", None)
        triggerType = kwargs.pop("triggerType", AnalogTriggerOutput.AnalogTriggerType.STATE)

        if kwargs:
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

        # positional arguments
        if len(args) == 1:
            if hasattr(args[0], "getChannelForRouting"):
                source = args[0]
            elif hasattr(args[0], "createOutput"):
                analogTrigger = args[0]
            else:
                channel = args[0]
        elif len(args) == 2:
            # analogTrigger assumed
            if not hasattr(args[0], "createOutput"):
                raise ValueError("expected AnalogTrigger when 2 arguments used")
            analogTrigger, triggerType = args
        else:
            raise ValueError("don't know how to handle %d positional arguments" % len(args))

        # convert channel into source
        if source is None:
            if channel is not None:
                source = DigitalInput(channel)
            elif analogTrigger is not None:
                source = analogTrigger.createOutput(triggerType)
            else:
                raise ValueError("didn't specify source")

        # save and set
        self.upSource = source
        hal.setCounterUpSource(self.counter,
                               self.upSource.getChannelForRouting(),
                               self.upSource.getAnalogTriggerForRouting())

    def setUpSourceEdge(self, risingEdge, fallingEdge):
        """Set the edge sensitivity on an up counting source. Set the up
        source to either detect rising edges or falling edges.

        :param risingEdge: True to count rising edge
        :param fallingEdge: True to count falling edge
        """
        if self.upSource is None:
            raise ValueError("Up Source must be set before setting the edge")
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterUpSourceEdge(self.counter, risingEdge, fallingEdge)

    def clearUpSource(self):
        """Disable the up counting source to the counter.
        """
        self.upSource = None
        if self.counter is None:
            return
        hal.clearCounterUpSource(self.counter)

    def setDownSource(self, *args, **kwargs):
        """Set the down counting source for the counter.

        This function accepts either a digital channel index, a
        `DigitalSource`, or an `AnalogTrigger` as positional arguments:
        
        - source
        - channel
        - analogTrigger, triggerType

        For positional arguments, if the passed object has a
        `getChannelForRouting` function, it is assumed to be a DigitalSource.
        If the passed object has a `createOutput` function, it is assumed to
        be an AnalogTrigger.

        Alternatively, sources and/or channels may be passed as keyword
        arguments.  The behavior of specifying both a source and a number
        for the same channel is undefined, as is passing both a positional
        and a keyword argument for the same channel.

        :param channel: the digital port to count
        :param source: the digital source to count
        :param analogTrigger:
            The analog trigger object that is used for the Up Source
        :param triggerType:
            The analog trigger output that will trigger the counter.
            Defaults to kState if not specified.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")

        # keyword arguments
        source = kwargs.pop("source", None)
        channel = kwargs.pop("channel", None)
        analogTrigger = kwargs.pop("analogTrigger", None)
        triggerType = kwargs.pop("triggerType", AnalogTriggerOutput.AnalogTriggerType.STATE)

        if kwargs:
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

        # positional arguments
        if len(args) == 1:
            if hasattr(args[0], "getChannelForRouting"):
                source = args[0]
            elif hasattr(args[0], "createOutput"):
                analogTrigger = args[0]
            else:
                channel = args[0]
        elif len(args) == 2:
            # analogTrigger assumed
            if not hasattr(args[0], "createOutput"):
                raise ValueError("expected AnalogTrigger when 2 arguments used")
            analogTrigger, triggerType = args
        else:
            raise ValueError("don't know how to handle %d positional arguments" % len(args))

        # convert channel into source
        if source is None:
            if channel is not None:
                source = DigitalInput(channel)
            elif analogTrigger is not None:
                source = analogTrigger.createOutput(triggerType)
            else:
                raise ValueError("didn't specify source")

        # save and set
        self.downSource = source
        hal.setCounterDownSource(self.counter,
                                 self.downSource.getChannelForRouting(),
                                 self.downSource.getAnalogTriggerForRouting())

    def setDownSourceEdge(self, risingEdge, fallingEdge):
        """Set the edge sensitivity on an down counting source. Set the down
        source to either detect rising edges or falling edges.

        :param risingEdge: True to count rising edge
        :param fallingEdge: True to count falling edge
        """
        if self.downSource is None:
            raise ValueError("Down Source must be set before setting the edge")
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterDownSourceEdge(self.counter, risingEdge, fallingEdge)

    def clearDownSource(self):
        """Disable the down counting source to the counter.
        """
        self.downSource = None
        if self.counter is None:
            return
        hal.clearCounterDownSource(self.counter)

    def setUpDownCounterMode(self):
        """Set standard up / down counting mode on this counter. Up and down
        counts are sourced independently from two inputs.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterUpDownMode(self.counter)

    def setExternalDirectionMode(self):
        """Set external direction mode on this counter. Counts are sourced on
        the Up counter input. The Down counter input represents the direction
        to count.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterExternalDirectionMode(self.counter)

    def setSemiPeriodMode(self, highSemiPeriod):
        """Set Semi-period mode on this counter. Counts up on both rising and
        falling edges.

        :param highSemiPeriod: True to count up on both rising and falling
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterSemiPeriodMode(self.counter, highSemiPeriod)

    def setPulseLengthMode(self, threshold):
        """Configure the counter to count in up or down based on the length
        of the input pulse. This mode is most useful for direction sensitive
        gear tooth sensors.

        :param threshold: The pulse length beyond which the counter counts the
            opposite direction. Units are seconds.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterPulseLengthMode(self.counter, threshold)

    def get(self):
        """Read the current counter value. Read the value at this instant. It
        may still be running, so it reflects the current value. Next time it
        is read, it might have a different value.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        return hal.getCounter(self.counter)

    def getDistance(self):
        """Read the current scaled counter value. Read the value at this
        instant, scaled by the distance per pulse (defaults to 1).

        :returns: Scaled value
        """
        return self.get() * self.distancePerPulse

    def reset(self):
        """Reset the Counter to zero. Set the counter value to zero. This
        doesn't effect the running state of the counter, just sets the
        current value to zero.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.resetCounter(self.counter)

    def setMaxPeriod(self, maxPeriod):
        """Set the maximum period where the device is still considered
        "moving".  Sets the maximum period where the device is considered
        moving. This value is used to determine the "stopped" state of the
        counter using the :func:`getStopped` method.

        :param maxPeriod: The maximum period where the counted device is
            considered moving in seconds.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterMaxPeriod(self.counter, maxPeriod)

    def setUpdateWhenEmpty(self, enabled):
        """Select whether you want to continue updating the event timer
        output when there are no samples captured. The output of the event
        timer has a buffer of periods that are averaged and posted to a
        register on the FPGA. When the timer detects that the event source
        has stopped (based on the MaxPeriod) the buffer of samples to be
        averaged is emptied. If you enable update when empty, you will be
        notified of the stopped source and the event time will report 0
        samples. If you disable update when empty, the most recent average
        will remain on the output until a new sample is acquired. You will
        never see 0 samples output (except when there have been no events
        since an FPGA reset) and you will likely not see the stopped bit
        become true (since it is updated at the end of an average and
        there are no samples to average).

        :param enabled: True to continue updating
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterUpdateWhenEmpty(self.counter, enabled)

    def getStopped(self):
        """Determine if the clock is stopped. Determine if the clocked input
        is stopped based on the MaxPeriod value set using the
        :func:`setMaxPeriod` method.  If the clock exceeds the MaxPeriod,
        then the device (and counter) are assumed to be stopped and it
        returns True.

        :returns: Returns True if the most recent counter period exceeds the
            MaxPeriod value set by SetMaxPeriod.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        return hal.getCounterStopped(self.counter)

    def getDirection(self):
        """The last direction the counter value changed.

        :returns: The last direction the counter value changed.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        return hal.getCounterDirection(self.counter)

    def setReverseDirection(self, reverseDirection):
        """Set the Counter to return reversed sensing on the direction. This
        allows counters to change the direction they are counting in the case
        of 1X and 2X quadrature encoding only. Any other counter mode isn't
        supported.

        :param reverseDirection: True if the value counted should be negated.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterReverseDirection(self.counter, reverseDirection)

    def getPeriod(self):
        """Get the Period of the most recent count. Returns the time interval
        of the most recent count. This can be used for velocity calculations
        to determine shaft speed.

        :returns: The period of the last two pulses in units of seconds.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        return hal.getCounterPeriod(self.counter)

    def getRate(self):
        """Get the current rate of the Counter. Read the current rate of the
        counter accounting for the distance per pulse value. The default
        value for distance per pulse (1) yields units of pulses per second.

        :returns: The rate in units/sec
        """
        return self.distancePerPulse / self.getPeriod()

    def setSamplesToAverage(self, samplesToAverage):
        """Set the Samples to Average which specifies the number of samples
        of the timer to average when calculating the period. Perform averaging
        to account for mechanical imperfections or as oversampling to increase
        resolution.

        :param samplesToAverage:
            The number of samples to average from 1 to 127.
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterSamplesToAverage(self.counter, samplesToAverage)

    def getSamplesToAverage(self):
        """Get the Samples to Average which specifies the number of samples
        of the timer to average when calculating the period. Perform averaging
        to account for mechanical imperfections or as oversampling to increase
        resolution.

        :returns: The number of samples being averaged (from 1 to 127)
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        return hal.getCounterSamplesToAverage(self.counter)

    def setDistancePerPulse(self, distancePerPulse):
        """Set the distance per pulse for this counter. This sets the
        multiplier used to determine the distance driven based on the count
        value from the encoder. Set this value based on the Pulses per
        Revolution and factor in any gearing reductions. This distance can be
        in any units you like, linear or angular.

        :param distancePerPulse:
            The scale factor that will be used to convert pulses to useful
            units.
        """
        self.distancePerPulse = distancePerPulse

    def setPIDSourceParameter(self, pidSource):
        """Set which parameter of the encoder you are using as a process
        control variable. The counter class supports the rate and distance
        parameters.

        :param pidSource: An enum to select the parameter.
        """
        if pidSource not in (0, 1):
            raise ValueError("invalid pidSource: %s" % pidSource)
        self.pidSource = pidSource

    def pidGet(self):
        if self.pidSource == self.PIDSourceParameter.kDistance:
            return self.getDistance()
        elif self.pidSource == self.PIDSourceParameter.kRate:
            return self.getRate()
        else:
            return 0.0

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Counter"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.get())

    def startLiveWindowMode(self):
        pass

    def stopLiveWindowMode(self):
        pass
