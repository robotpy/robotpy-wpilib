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
from .counter import Counter
from .digitalinput import DigitalInput
from .livewindow import LiveWindow
from .resource import Resource
from .sensorbase import SensorBase

from ._impl.utils import match_arglist, HasAttribute

__all__ = ["Encoder"]

def _freeEncoder(encoder):
    hal.freeEncoder(encoder)

class Encoder(SensorBase):
    """Reads from quadrature encoders.
    
    Quadrature encoders are devices that count
    shaft rotation and can sense direction. The output of the QuadEncoder class
    is an integer that can count either up or down, and can go negative for
    reverse direction counting. When creating QuadEncoders, a direction is
    supplied that changes the sense of the output to make code more readable
    if the encoder is mounted such that forward movement generates negative
    values. Quadrature encoders have two digital outputs, an A Channel and a
    B Channel that are out of phase with each other to allow the FPGA to do
    direction sensing.

    All encoders will immediately start counting - reset() them if you need
    them to be zeroed before use.

    Instance variables:
    
    - aSource: The A phase of the quad encoder
    - bSource: The B phase of the quad encoder
    - indexSource: The index source (available on some encoders)
    
    .. not_implemented: initEncoder
    """

    class IndexingType:
        kResetWhileHigh = 0
        kResetWhileLow = 1
        kResetOnFallingEdge = 2
        kResetOnRisingEdge = 3

    EncodingType = CounterBase.EncodingType
    PIDSourceParameter = PIDSource.PIDSourceParameter

    def __init__(self, *args, **kwargs):
        """Encoder constructor. Construct a Encoder given a and b channels
        and optionally an index channel.

        The encoder will start counting immediately.

        The a, b, and optional index channel arguments may be either channel
        numbers or `DigitalSource` sources. There may also be a boolean
        reverseDirection, and an encodingType according to the following
        list.
        
        - aSource, bSource
        - aSource, bSource, reverseDirection
        - aSource, bSource, reverseDirection, encodingType
        - aSource, bSource, indexSource, reverseDirection
        - aSource, bSource, indexSource
        - aChannel, bChannel
        - aChannel, bChannel, reverseDirection
        - aChannel, bChannel, reverseDirection, encodingType
        - aChannel, bChannel, indexChannel, reverseDirection
        - aChannel, bChannel, indexChannel

        For positional arguments, if the passed object has a
        `getChannelForRouting` function, it is assumed to be a DigitalSource.

        Alternatively, sources and/or channels may be passed as keyword
        arguments.  The behavior of specifying both a source and a number
        for the same channel is undefined, as is passing both a positional
        and a keyword argument for the same channel.

        In addition, keyword parameters may be provided for reverseDirection
        and inputType.

        :param aSource: The source that should be used for the a channel.
        :param bSource: The source that should be used for the b channel.
        :param indexSource: The source that should be used for the index
            channel.
        :param aChannel: The digital input index that should be used for
            the a channel.
        :param bChannel: The digital input index that should be used for
            the b channel.
        :param indexChannel: The digital input index that should be used
            for the index channel.
        :param reverseDirection:
            Represents the orientation of the encoder and inverts the
            output values if necessary so forward represents positive
            values.  Defaults to False if unspecified.
        :param encodingType:
            Either k1X, k2X, or k4X to indicate 1X, 2X or 4X decoding. If
            4X is selected, then an encoder FPGA object is used and the
            returned counts will be 4x the encoder spec'd value since all
            rising and falling edges are counted. If 1X or 2X are selected
            then a counter object will be used and the returned value will
            either exactly match the spec'd count or be double (2x) the
            spec'd count.  Defaults to k4X if unspecified.
        :type encodingType: :class:`Encoder.EncodingType`
        """
        a_source_arg = ("aSource", HasAttribute("getChannelForRouting"))
        b_source_arg = ("bSource", HasAttribute("getChannelForRouting"))
        index_source_arg = ("indexSource", HasAttribute("getChannelForRouting"))
        a_channel_arg = ("aChannel", int)
        b_channel_arg = ("bChannel", int)
        index_channel_arg = ("indexChannel", int)

        argument_templates = [[a_source_arg, b_source_arg],
                              [a_source_arg, b_source_arg, ("reverseDirection", bool)],
                              [a_source_arg, b_source_arg, ("reverseDirection", bool), ("encodingType", int)],
                              [a_source_arg, b_source_arg, index_source_arg],
                              [a_source_arg, b_source_arg, index_source_arg, ("reverseDirection", bool)],
                              [a_channel_arg, b_channel_arg],
                              [a_channel_arg, b_channel_arg, ("reverseDirection", bool)],
                              [a_channel_arg, b_channel_arg, ("reverseDirection", bool), ("encodingType", int)],
                              [a_channel_arg, b_channel_arg, index_channel_arg],
                              [a_channel_arg, b_channel_arg, index_channel_arg, ("reverseDirection", bool)]]

        _, results = match_arglist('Encoder.__init__',
                                   args, kwargs, argument_templates)
        
        # keyword arguments
        aSource = results.pop("aSource", None)
        bSource = results.pop("bSource", None)
        indexSource = results.pop("indexSource", None)
        aChannel = results.pop("aChannel", None)
        bChannel = results.pop("bChannel", None)
        indexChannel = results.pop("indexChannel", None)
        reverseDirection = results.pop("reverseDirection", False)
        encodingType = results.pop("encodingType", self.EncodingType.k4X)

        # convert channels into sources
        self.allocatedA = False
        self.allocatedB = False
        self.allocatedIndex = False

        if aSource is None:
            if aChannel is None:
                raise ValueError("didn't specify A channel")
            aSource = DigitalInput(aChannel)
            self.allocatedA = True
        if bSource is None:
            if bChannel is None:
                raise ValueError("didn't specify B channel")
            bSource = DigitalInput(bChannel)
            self.allocatedB = True
        if indexSource is None and indexChannel is not None:
            indexSource = DigitalInput(indexChannel)
            self.allocatedIndex = True

        # save to instance variables
        self.aSource = aSource
        self.bSource = bSource
        self.indexSource = indexSource
        self.encodingType = encodingType
        self.distancePerPulse = 1.0 # distance of travel for each encoder tick
        self.pidSource = PIDSource.PIDSourceParameter.kDistance
        self._encoder = None
        self.counter = None
        self.index = 0

        if encodingType == self.EncodingType.k4X:
            self._encoder, self.index = hal.initializeEncoder(
                    aSource.getModuleForRouting(),
                    aSource.getChannelForRouting(),
                    aSource.getAnalogTriggerForRouting(),
                    bSource.getModuleForRouting(),
                    bSource.getChannelForRouting(),
                    bSource.getAnalogTriggerForRouting(),
                    reverseDirection)
            self._encoder_finalizer = \
                    weakref.finalize(self, _freeEncoder, self._encoder)
            self.setMaxPeriod(.5)
            self.encodingScale = 4
        elif encodingType in (self.EncodingType.k2X, self.EncodingType.k1X):
            # Use Counter object for 1x and 2x encoding
            self.counter = Counter(encodingType, aSource, bSource,
                                   reverseDirection)
            if encodingType == self.encodingType.k2X:
                self.encodingScale = 2
            else:
                self.encodingScale = 1
            self.index = self.counter.getFPGAIndex()
        else:
            raise ValueError("unrecognized encodingType: %s" % encodingType)
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)
        
        if self.indexSource is not None:
            self.setIndexSource(self.indexSource)

        hal.HALReport(hal.HALUsageReporting.kResourceType_Encoder,
                      self.index, encodingType)
        LiveWindow.addSensorChannel("Encoder", aSource.getChannelForRouting(),
                                    self)

    @property
    def encoder(self):
        if not self._encoder_finalizer.alive:
            return None
        return self._encoder

    def getFPGAIndex(self):
        """
        :returns: The Encoder's FPGA index
        """
        return self.index

    def getEncodingScale(self):
        """
        :returns: The encoding scale factor 1x, 2x, or 4x, per the requested
            encodingType. Used to divide raw edge counts down to spec'd counts.
        """
        return self.encodingScale

    def free(self):
        if self.aSource is not None and self.allocatedA:
            self.aSource.free()
            self.allocatedA = False
        if self.bSource is not None and self.allocatedB:
            self.bSource.free()
            self.allocatedB = False
        if self.indexSource is not None and self.allocatedIndex:
            self.indexSource.free()
            self.allocatedIndex = False
        self.aSource = None
        self.bSource = None
        self.indexSource = None
        if self.counter is not None:
            self.counter.free()
            self.counter = None
        else:
            self._encoder_finalizer()

    def getRaw(self):
        """Gets the raw value from the encoder. The raw value is the actual
        count unscaled by the 1x, 2x, or 4x scale factor.

        :returns: Current raw count from the encoder
        """
        if self.counter is not None:
            return self.counter.get()
        return hal.getEncoder(self.encoder)

    def get(self):
        """Gets the current count. Returns the current count on the Encoder.
        This method compensates for the decoding type.

        :returns: Current count from the Encoder adjusted for the 1x, 2x, or
            4x scale factor.
        """
        return int(self.getRaw() * self.decodingScaleFactor())

    def reset(self):
        """Reset the Encoder distance to zero. Resets the current count to
        zero on the encoder.
        """
        if self.counter is not None:
            self.counter.reset()
        elif self.encoder is not None:
            hal.resetEncoder(self.encoder)
        else:
            raise ValueError("operation on freed port")

    def getPeriod(self):
        """Returns the period of the most recent pulse. Returns the period of
        the most recent Encoder pulse in seconds. This method compensates for
        the decoding type.

        .. deprecated::
            Use :func:`getRate` in favor of this method. This returns unscaled
            periods and :func:`getRate` scales using value from
            :func:`getDistancePerPulse`.

        :returns: Period in seconds of the most recent pulse.
        """
        warnings.warn("use getRate instead", DeprecationWarning)
        if self.counter is not None:
            measuredPeriod = self.counter.getPeriod() / self.decodingScaleFactor()
        elif self.encoder is not None:
            measuredPeriod = hal.getEncoderPeriod(self.encoder)
        else:
            raise ValueError("operation on freed port")
        return measuredPeriod

    def setMaxPeriod(self, maxPeriod):
        """Sets the maximum period for stopped detection. Sets the value that
        represents the maximum period of the Encoder before it will assume
        that the attached device is stopped. This timeout allows users to
        determine if the wheels or other shaft has stopped rotating. This
        method compensates for the decoding type.

        :param maxPeriod: The maximum time between rising and falling edges
            before the FPGA will report the device stopped. This is expressed
            in seconds.
        """
        if self.counter is not None:
            self.counter.setMaxPeriod(maxPeriod * self.decodingScaleFactor())
        elif self.encoder is not None:
            hal.setEncoderMaxPeriod(self.encoder, maxPeriod)
        else:
            raise ValueError("operation on freed port")

    def getStopped(self):
        """Determine if the encoder is stopped. Using the MaxPeriod value, a
        boolean is returned that is True if the encoder is considered stopped
        and False if it is still moving. A stopped encoder is one where the
        most recent pulse width exceeds the MaxPeriod.

        :returns: True if the encoder is considered stopped.
        """
        if self.counter is not None:
            return self.counter.getStopped()
        elif self.encoder is not None:
            return hal.getEncoderStopped(self.encoder)
        else:
            raise ValueError("operation on freed port")

    def getDirection(self):
        """The last direction the encoder value changed.

        :returns: The last direction the encoder value changed.
        """
        if self.counter is not None:
            return self.counter.getDirection()
        return hal.getEncoderDirection(self.encoder)

    def decodingScaleFactor(self):
        """The scale needed to convert a raw counter value into a number of
        encoder pulses.
        """
        if self.encodingType == self.EncodingType.k1X:
            return 1.0
        elif self.encodingType == self.EncodingType.k2X:
            return 0.5
        elif self.encodingType == self.EncodingType.k4X:
            return 0.25
        else:
            raise ValueError("unexpected encodingType: %d" % self.encodingType)

    def getDistance(self):
        """Get the distance the robot has driven since the last reset.

        :returns: The distance driven since the last reset as scaled by the
            value from :func:`setDistancePerPulse`.
        """
        return self.getRaw() * self.decodingScaleFactor() * self.distancePerPulse

    def getRate(self):
        """Get the current rate of the encoder. Units are distance per second
        as scaled by the value from :func:`setDistancePerPulse`.

         :returns: The current rate of the encoder.
        """
        return self.distancePerPulse / self.getPeriod()

    def setMinRate(self, minRate):
        """Set the minimum rate of the device before the hardware reports it
        stopped.

        :param minRate: The minimum rate. The units are in distance per
            second as scaled by the value from :func:`setDistancePerPulse`.
        """
        self.setMaxPeriod(self.distancePerPulse / minRate)

    def setDistancePerPulse(self, distancePerPulse):
        """Set the distance per pulse for this encoder. This sets the
        multiplier used to determine the distance driven based on the count
        value from the encoder. Do not include the decoding type in this
        scale. The library already compensates for the decoding type. Set
        this value based on the encoder's rated Pulses per Revolution and
        factor in gearing reductions following the encoder shaft. This
        distance can be in any units you like, linear or angular.

        :param distancePerPulse: The scale factor that will be used to convert
            pulses to useful units.
        """
        self.distancePerPulse = distancePerPulse

    def setReverseDirection(self, reverseDirection):
        """Set the direction sensing for this encoder. This sets the direction
        sensing on the encoder so that it could count in the correct software
        direction regardless of the mounting.

        :param reverseDirection: True if the encoder direction should be
            reversed
        """
        if self.counter is not None:
            self.counter.setReverseDirection(reverseDirection)
        else:
            raise NotImplementedError # FIXME?

    def setSamplesToAverage(self, samplesToAverage):
        """Set the Samples to Average which specifies the number of samples
        of the timer to average when calculating the period. Perform averaging
        to account for mechanical imperfections or as oversampling to increase
        resolution.

        TODO: Should this raise an exception, so that the user has to
        deal with giving an incorrect value?

        :param samplesToAverage: The number of samples to average from 1 to
            127.
        """
        if self.encodingType == self.EncodingType.k4X:
            hal.setEncoderSamplesToAverage(self.encoder, samplesToAverage)
        elif self.encodingType in (self.EncodingType.k2X,
                                   self.EncodingType.k1X):
            self.counter.setSamplesToAverage(samplesToAverage)

    def getSamplesToAverage(self):
        """Get the Samples to Average which specifies the number of samples
        of the timer to average when calculating the period. Perform averaging
        to account for mechanical imperfections or as oversampling to increase
        resolution.

        :returns: The number of samples being averaged (from 1 to 127)
        """
        if self.encodingType.value == self.EncodingType.k4X:
            return hal.getEncoderSamplesToAverage(self.encoder)
        elif self.encodingType in (self.EncodingType.k2X,
                                   self.EncodingType.k1X):
            return self.counter.getSamplesToAverage()
        else:
            return 1

    def setPIDSourceParameter(self, pidSource):
        """Set which parameter of the encoder you are using as a process
        control variable. The encoder class supports the rate and distance
        parameters.

        :param pidSource: An enum to select the parameter.
        """
        if pidSource not in (0, 1):
            raise ValueError("invalid pidSource: %s" % pidSource)
        self.pidSource = pidSource

    def pidGet(self):
        """Implement the PIDSource interface.

         :returns: The current value of the selected source parameter.
        """
        if self.pidSource == self.PIDSourceParameter.kDistance:
            return self.getDistance()
        elif self.pidSource == self.PIDSourceParameter.kRate:
            return self.getRate()
        else:
            return 0.0

    def setIndexSource(self, source, indexing_type=IndexingType.kResetOnRisingEdge):
        """
        Set the index source for the encoder. When this source rises, the encoder count automatically resets.

        :param source: Either an initialized DigitalSource or a DIO channel number
        :type: Either a :class:`wpilib.DigitalInput` or number
        :param indexing_type: The state that will cause the encoder to reset
        :type: A value from :class:`wpilib.DigitalInput.IndexingType`
        """
        if hasattr(source, "getChannelForRouting"):
            self.indexSource = source
        else:
            self.indexSource = DigitalInput(source)

        activeHigh = (indexing_type == self.IndexingType.kResetWhileHigh or indexing_type == self.IndexingType.kResetOnRisingEdge)
        edgeSensitive = (indexing_type == self.IndexingType.kResetOnFallingEdge or indexing_type == self.IndexingType.kResetOnRisingEdge)
        
        hal.setEncoderIndexSource(self.encoder, self.indexSource.getChannelForRouting(),
                                  self.indexSource.getAnalogTriggerForRouting(), activeHigh, edgeSensitive)

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        if self.encodingType == self.EncodingType.k4X:
            return "Quadrature Encoder"
        return "Encoder"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Speed", self.getRate())
            table.putNumber("Distance", self.getDistance())
            table.putNumber("Distance per Tick", self.distancePerPulse)

    def startLiveWindowMode(self):
        pass

    def stopLiveWindowMode(self):
        pass
