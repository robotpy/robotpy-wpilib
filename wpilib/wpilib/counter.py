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
from ._impl.utils import match_arglist, HasAttribute

__all__ = ["Counter"]

def _freeCounter(counter):
    hal.setCounterUpdateWhenEmpty(counter, True)
    hal.clearCounterUpSource(counter)
    hal.clearCounterDownSource(counter)
    hal.freeCounter(counter)

class Counter(SensorBase):
    """Counts the number of ticks on a :class:`.DigitalInput` channel.
    
    This is a general purpose class for counting repetitive events. It can return
    the number of counts, the period of the most recent cycle, and detect when
    the signal being counted has stopped by supplying a maximum cycle time.

    All counters will immediately start counting - :meth:`reset` them if you need
    them to be zeroed before use.
    
    .. not_implemented: initCounter
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
    allocatedUpSource = False
    allocatedDownSource = False

    def __init__(self, *args, **kwargs):
        """Counter constructor.

        The counter will start counting immediately.

        Positional arguments may be either channel numbers, :class:`.DigitalSource`
        sources, or :class:`.AnalogTrigger` sources in the following order:

        A "source" is any valid single-argument input to :meth:`setUpSource` and :meth:`setDownSource`
        
        - (none)
        - upSource
        - upSource, down source
        And, to keep consistency with Java wpilib.
        - encodingType, up source, down source, inverted

        If the passed object has a
        `getChannelForRouting` function, it is assumed to be a DigitalSource.
        If the passed object has a `createOutput` function, it is assumed to
        be an AnalogTrigger.

        In addition, extra keyword parameters may be provided for mode, inverted,
        and encodingType.

        :param upSource: The source (channel num, DigitalInput, or AnalogTrigger)
            that should be used for up counting.
        :param downSource: The source (channel num, DigitalInput, or AnalogTrigger)
            that should be used for down counting or direction control.
        :param mode:
            How and what the counter counts (see :class:`.Mode`).  Defaults to
            `Mode.kTwoPulse` for zero or one source, and
            `Mode.kExternalDirection` for two sources.
        :param inverted:
            Flips the direction of counting.  Defaults to False if unspecified.
            Only used when two sources are specified.
        :param encodingType:
            Either k1X or k2X to indicate 1X or 2X decoding. 4X decoding
            is not supported by Counter; use `Encoder` instead.  Defaults
            to k1X if unspecified.  Only used when two sources are specified.
        """

        source_identifier = [int, HasAttribute("getChannelForRouting"), HasAttribute("createOutput")]

        argument_templates = [[],
                              [("upSource", source_identifier), ],
                              [("upSource", source_identifier), ("downSource", source_identifier)],
                              [("encodingType", None), ("upSource", source_identifier),
                               ("downSource", source_identifier), ("inverted", bool)], ]


        _, results = match_arglist('Counter.__init__',
                                   args, kwargs, argument_templates, allow_extra_kwargs=True)

        # extract arguments
        upSource = results.pop("upSource", None)
        downSource = results.pop("downSource", None)

        encodingType = results.pop("encodingType", None)
        inverted = results.pop("inverted", False)
        mode = results.pop("mode", None)

        if mode is None:
            #Get the mode
            if upSource is not None and downSource is not None:
                mode = self.Mode.kExternalDirection
            else:
                mode = self.Mode.kTwoPulse

        # save some variables
        self.distancePerPulse = 1.0 # distance of travel for each tick
        self.pidSource = PIDSource.PIDSourceParameter.kDistance

        # create counter
        self._counter, self.index = hal.initializeCounter(mode)
        self._counter_finalizer = \
            weakref.finalize(self, _freeCounter, self._counter)

        self.setMaxPeriod(.5)

        hal.HALReport(hal.HALUsageReporting.kResourceType_Counter, self.index,
                      mode)

        #Set sources
        if upSource is not None:
            self.setUpSource(upSource)

        if downSource is not None:
            self.setDownSource(downSource)

        # when given two sources, set edges
        if upSource is not None and downSource is not None:
            if encodingType == self.EncodingType.k1X:
                self.setUpSourceEdge(True, False)
                hal.setCounterAverageSize(self._counter, 1)
            else:
                self.setUpSourceEdge(True, True)
                hal.setCounterAverageSize(self._counter, 2)
            self.setDownSourceEdge(inverted, True)

    @property
    def counter(self):
        if not self._counter_finalizer.alive:
            return None
        return self._counter

    def free(self):
        self.setUpdateWhenEmpty(True)
        self.clearUpSource()

        self.clearDownSource()
        self._counter_finalizer()

    def getFPGAIndex(self):
        """
        :returns: The Counter's FPGA index.
        """
        return self.index

    def setUpSource(self, *args, **kwargs):
        """Set the up counting source for the counter.

        This function accepts either a digital channel index, a
        `DigitalSource`, or an `AnalogTrigger` as positional arguments:

        - source
        - channel
        - analogTrigger
        - analogTrigger, triggerType

        For positional arguments, if the passed object has a
        `getChannelForRouting` function, it is assumed to be a DigitalSource.
        If the passed object has a `createOutput` function, it is assumed to
        be an AnalogTrigger.

        Alternatively, sources and/or channels may be passed as keyword
        arguments.  The behavior of specifying both a source and a number
        for the same channel is undefined, as is passing both a positional
        and a keyword argument for the same channel.

        :param channel: the DIO channel to use as the up source. 0-9 are on-board, 10-25 are on the MXP
        :type channel: int
        :param source: The digital source to count
        :type source: DigitalInput
        :param analogTrigger:
            The analog trigger object that is used for the Up Source
        :type analogTrigger: AnalogTrigger
        :param triggerType:
            The analog trigger output that will trigger the counter.
            Defaults to kState if not specified.
        :type triggerType: AnalogTriggerType
        """

        #TODO Both this and the java implementation should probably not allow setting a source if one is already set.

        if self.counter is None:
            raise ValueError("operation on freed port")

        argument_templates = [[("channel", int)],
                              [("source", HasAttribute("getChannelForRouting")), ],
                              [("analogTrigger", HasAttribute("createOutput"))],
                              [("analogTrigger", HasAttribute("createOutput")), ("triggerType", None)]]

        _, results = match_arglist('Counter.setUpSource',
                                   args, kwargs, argument_templates)

        # extract arguments
        source = results.pop("source", None)
        channel = results.pop("channel", None)
        analogTrigger = results.pop("analogTrigger", None)
        triggerType = results.pop("triggerType", AnalogTriggerOutput.AnalogTriggerType.kState)

        # If we don't have source, generate it from other arguments.
        if source is None:
            if channel is not None:
                source = DigitalInput(channel)
                self.allocatedUpSource = True
            elif analogTrigger is not None and triggerType is not None:
                source = analogTrigger.createOutput(triggerType)
            else:
                raise ValueError("No usable source.")

        # save and set
        self.upSource = source
        hal.setCounterUpSource(self.counter,
                               self.upSource.getChannelForRouting(),
                               self.upSource.getAnalogTriggerForRouting())

    def setUpSourceEdge(self, risingEdge, fallingEdge):
        """Set the edge sensitivity on an up counting source. Set the up
        source to either detect rising edges or falling edges.

        :param risingEdge: True to count rising edge
        :type  risingEdge: bool
        :param fallingEdge: True to count falling edge
        :type  fallingEdge: bool
        """
        if self.upSource is None:
            raise ValueError("Up Source must be set before setting the edge")
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterUpSourceEdge(self.counter, risingEdge, fallingEdge)

    def clearUpSource(self):
        """Disable the up counting source to the counter."""
        if self.upSource is not None and self.allocatedUpSource:
            self.upSource.free()
            self.allocatedUpSource = False
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
        - analogTrigger
        - analogTrigger, triggerType

        For positional arguments, if the passed object has a
        `getChannelForRouting` function, it is assumed to be a DigitalSource.
        If the passed object has a `createOutput` function, it is assumed to
        be an AnalogTrigger.

        Alternatively, sources and/or channels may be passed as keyword
        arguments.  The behavior of specifying both a source and a number
        for the same channel is undefined, as is passing both a positional
        and a keyword argument for the same channel.

        :param channel: the DIO channel to use as the down source. 0-9 are on-board, 10-25 are on the MXP
        :type channel: int
        :param source: The digital source to count
        :type source: DigitalInput
        :param analogTrigger:
            The analog trigger object that is used for the Up Source
        :type analogTrigger: AnalogTrigger
        :param triggerType:
            The analog trigger output that will trigger the counter.
            Defaults to kState if not specified.
        :type triggerType: AnalogTriggerType
        """

        #TODO Both this and the java implementation should probably not allow setting a source if one is already set.

        if self.counter is None:
            raise ValueError("operation on freed port")

        argument_templates = [[("channel", int)],
                              [("source", HasAttribute("getChannelForRouting")), ],
                              [("analogTrigger", HasAttribute("createOutput")), ],
                              [("analogTrigger", HasAttribute("createOutput")), ("triggerType", None)]]

        _, results = match_arglist('Counter.setUpSource',
                                   args, kwargs, argument_templates)

        # extract arguments
        source = results.pop("source", None)
        channel = results.pop("channel", None)
        analogTrigger = results.pop("analogTrigger", None)
        triggerType = results.pop("triggerType", AnalogTriggerOutput.AnalogTriggerType.kState)

        # If we don't have source, generate it from other arguments.
        if source is None:
            if channel is not None:
                source = DigitalInput(channel)
                self.allocatedDownSource = True
            elif analogTrigger is not None and triggerType is not None:
                source = analogTrigger.createOutput(triggerType)
            else:
                raise ValueError("No usable source.")

        # save and set
        self.downSource = source
        hal.setCounterDownSource(self.counter,
                                 self.downSource.getChannelForRouting(),
                                 self.downSource.getAnalogTriggerForRouting())

    def setDownSourceEdge(self, risingEdge, fallingEdge):
        """Set the edge sensitivity on an down counting source. Set the down
        source to either detect rising edges or falling edges.

        :param risingEdge: True to count rising edge
        :type  risingEdge: bool
        :param fallingEdge: True to count falling edge
        :type  fallingEdge: bool
        """
        if self.downSource is None:
            raise ValueError("Down Source must be set before setting the edge")
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterDownSourceEdge(self.counter, risingEdge, fallingEdge)

    def clearDownSource(self):
        """Disable the down counting source to the counter.
        """
        if self.downSource is not None and self.allocatedDownSource:
            self.downSource.free()
            self.allocatedDownSource = False
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
        :type  highSemiPeriod: bool
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
        :type  threshold: float, int
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterPulseLengthMode(self.counter, float(threshold))

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
        :rtype: float
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
        :type maxPeriod: float or int
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterMaxPeriod(self.counter, float(maxPeriod))

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
        :type  enabled: bool
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
        :rtype: bool
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        return hal.getCounterStopped(self.counter)

    def getDirection(self):
        """The last direction the counter value changed.

        :returns: The last direction the counter value changed.
        :rtype: bool
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
        :type  reverseDirection: bool 
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        hal.setCounterReverseDirection(self.counter, reverseDirection)

    def getPeriod(self):
        """Get the Period of the most recent count. Returns the time interval
        of the most recent count. This can be used for velocity calculations
        to determine shaft speed.

        :returns: The period of the last two pulses in units of seconds.
        :rtype: float
        """
        if self.counter is None:
            raise ValueError("operation on freed port")
        return hal.getCounterPeriod(self.counter)

    def getRate(self):
        """Get the current rate of the Counter. Read the current rate of the
        counter accounting for the distance per pulse value. The default
        value for distance per pulse (1) yields units of pulses per second.

        :returns: The rate in units/sec
        :rtype: float
        """
        return self.distancePerPulse / self.getPeriod()

    def setSamplesToAverage(self, samplesToAverage):
        """Set the Samples to Average which specifies the number of samples
        of the timer to average when calculating the period. Perform averaging
        to account for mechanical imperfections or as oversampling to increase
        resolution.

        :param samplesToAverage: The number of samples to average from 1 to 127.
        :type  samplesToAverage: int
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
        :rtype: int
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
        :type  distancePerPulse: float
        """
        self.distancePerPulse = distancePerPulse

    def setPIDSourceParameter(self, pidSource):
        """Set which parameter of the encoder you are using as a process
        control variable. The counter class supports the rate and distance
        parameters.

        :param pidSource: An enum to select the parameter.
        :type  pidSource: :class:`Counter.PIDSourceParameter`
        """
        if pidSource not in (self.PIDSourceParameter.kDistance,
                             self.PIDSourceParameter.kRate):
            raise ValueError("Invalid pidSource argument '%s'" % pidSource)
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
