# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/Encoder.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Union

import hal
import warnings
import weakref
import enum

from .interfaces.counterbase import CounterBase
from .interfaces.pidsource import PIDSource
from .counter import Counter
from .digitalinput import DigitalInput
from .livewindow import LiveWindow
from .resource import Resource
from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder

from ._impl.utils import match_arglist, HasAttribute

__all__ = ["Encoder"]


def _freeEncoder(encoder: "Encoder") -> None:
    hal.freeEncoder(encoder)


class Encoder(SendableBase):
    """Class to read quadrature encoders.
    
    Quadrature encoders are devices that count
    shaft rotation and can sense direction. The output of the Encoder class
    is an integer that can count either up or down, and can go negative for
    reverse direction counting. When creating Encoders, a direction can be
    supplied that inverts the sense of the output to make code more readable
    if the encoder is mounted such that forward movement generates negative
    values. Quadrature encoders have two digital outputs, an A Channel and a
    B Channel, that are out of phase with each other for direction sensing.

    All encoders will immediately start counting - reset() them if you need
    them to be zeroed before use.

    Instance variables:
    
    - aSource: The A phase of the quad encoder
    - bSource: The B phase of the quad encoder
    - indexSource: The index source (available on some encoders)
    """

    class IndexingType(enum.IntEnum):
        kResetWhileHigh = 0
        kResetWhileLow = 1
        kResetOnFallingEdge = 2
        kResetOnRisingEdge = 3

    EncodingType = CounterBase.EncodingType
    PIDSourceType = PIDSource.PIDSourceType

    def __init__(self, *args, **kwargs) -> None:
        """Encoder constructor. Construct a Encoder given a and b channels
        and optionally an index channel.

        The encoder will start counting immediately.

        The a, b, and optional index channel arguments may be either channel
        numbers or :class:`.DigitalSource` sources. There may also be a boolean
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
        `getPortHandleForRouting` function, it is assumed to be a DigitalSource.

        Alternatively, sources and/or channels may be passed as keyword
        arguments.  The behavior of specifying both a source and a number
        for the same channel is undefined, as is passing both a positional
        and a keyword argument for the same channel.

        In addition, keyword parameters may be provided for reverseDirection
        and inputType.

        :param aSource: The source that should be used for the a channel.
        :type aSource: :class:`.DigitalSource`
        :param bSource: The source that should be used for the b channel.
        :type bSource: :class:`.DigitalSource`
        :param indexSource: The source that should be used for the index
            channel.
        :type indexSource: :class:`.DigitalSource`
        :param aChannel: The digital input index that should be used for
            the a channel.
        :type aChannel: int
        :param bChannel: The digital input index that should be used for
            the b channel.
        :type bChannel: int
        :param indexChannel: The digital input index that should be used
            for the index channel.
        :type indexChannel: int
        :param reverseDirection:
            Represents the orientation of the encoder and inverts the
            output values if necessary so forward represents positive
            values.  Defaults to False if unspecified.
        :type reverseDirection: bool
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
        super().__init__()
        a_source_arg = ("aSource", HasAttribute("getPortHandleForRouting"))
        b_source_arg = ("bSource", HasAttribute("getPortHandleForRouting"))
        index_source_arg = ("indexSource", HasAttribute("getPortHandleForRouting"))
        a_channel_arg = ("aChannel", int)
        b_channel_arg = ("bChannel", int)
        index_channel_arg = ("indexChannel", int)

        # fmt: off
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
        # fmt: on

        _, results = match_arglist("Encoder.__init__", args, kwargs, argument_templates)

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
            self.addChild(aSource)
        if bSource is None:
            if bChannel is None:
                raise ValueError("didn't specify B channel")
            bSource = DigitalInput(bChannel)
            self.allocatedB = True
            self.addChild(bSource)
        if indexSource is None and indexChannel is not None:
            indexSource = DigitalInput(indexChannel)
            self.allocatedIndex = True
            self.addChild(indexSource)

        # save to instance variables
        self.aSource = aSource
        self.bSource = bSource
        self.indexSource = indexSource
        self.encodingType = encodingType
        self.pidSource = self.PIDSourceType.kDisplacement
        self.encoder = None
        self.counter = None
        self.speedEntry = None
        self.distanceEntry = None
        self.distancePerTickEntry = None

        self.encoder = hal.initializeEncoder(
            aSource.getPortHandleForRouting(),
            aSource.getAnalogTriggerTypeForRouting(),
            bSource.getPortHandleForRouting(),
            bSource.getAnalogTriggerTypeForRouting(),
            reverseDirection,
            encodingType,
        )

        self.__finalizer = weakref.finalize(self, _freeEncoder, self.encoder)

        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        if self.indexSource is not None:
            self.setIndexSource(self.indexSource)

        self.index = self.getFPGAIndex()
        hal.report(hal.UsageReporting.kResourceType_Encoder, self.index, encodingType)
        self.setName("Encoder", self.index)

    def getFPGAIndex(self) -> int:
        """
        Get the FPGA Index of the encoder

        :returns: The Encoder's FPGA index
        """
        return hal.getEncoderFPGAIndex(self.encoder)

    def getEncodingScale(self) -> int:
        """
        :returns: The encoding scale factor 1x, 2x, or 4x, per the requested
            encodingType. Used to divide raw edge counts down to spec'd counts.
        """
        return hal.getEncoderEncodingScale(self.encoder)

    def close(self) -> None:
        """Free the resources used by this object."""
        super().close()
        if self.aSource is not None and self.allocatedA:
            self.aSource.close()
            self.allocatedA = False
        if self.bSource is not None and self.allocatedB:
            self.bSource.close()
            self.allocatedB = False
        if self.indexSource is not None and self.allocatedIndex:
            self.indexSource.close()
            self.allocatedIndex = False
        self.aSource = None
        self.bSource = None
        self.indexSource = None
        self.__finalizer()
        self.encoder = None

    def getRaw(self) -> int:
        """Gets the raw value from the encoder. The raw value is the actual
        count unscaled by the 1x, 2x, or 4x scale factor.

        :returns: Current raw count from the encoder
        """
        return hal.getEncoderRaw(self.encoder)

    def get(self) -> int:
        """Gets the current count. Returns the current count on the Encoder.
        This method compensates for the decoding type.

        :returns: Current count from the Encoder adjusted for the 1x, 2x, or
            4x scale factor.
        """
        return hal.getEncoder(self.encoder)

    def reset(self) -> None:
        """Reset the Encoder distance to zero. Resets the current count to
        zero on the encoder.
        """
        hal.resetEncoder(self.encoder)

    def getPeriod(self) -> float:
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
        return hal.getEncoderPeriod(self.encoder)

    def setMaxPeriod(self, maxPeriod: float) -> None:
        """Sets the maximum period for stopped detection. Sets the value that
        represents the maximum period of the Encoder before it will assume
        that the attached device is stopped. This timeout allows users to
        determine if the wheels or other shaft has stopped rotating. This
        method compensates for the decoding type.

        :param maxPeriod: The maximum time between rising and falling edges
            before the FPGA will report the device stopped. This is expressed
            in seconds.
        """
        hal.setEncoderMaxPeriod(self.encoder, maxPeriod)

    def getStopped(self) -> bool:
        """Determine if the encoder is stopped. Using the MaxPeriod value, a
        boolean is returned that is True if the encoder is considered stopped
        and False if it is still moving. A stopped encoder is one where the
        most recent pulse width exceeds the MaxPeriod.

        :returns: True if the encoder is considered stopped.
        """
        return hal.getEncoderStopped(self.encoder)

    def getDirection(self) -> bool:
        """The last direction the encoder value changed.

        :returns: The last direction the encoder value changed.
        """
        return hal.getEncoderDirection(self.encoder)

    def getDistance(self) -> float:
        """Get the distance the robot has driven since the last reset.

        :returns: The distance driven since the last reset as scaled by the
            value from :func:`setDistancePerPulse`.
        """
        return hal.getEncoderDistance(self.encoder)

    def getRate(self) -> float:
        """Get the current rate of the encoder. Units are distance per second
        as scaled by the value from :func:`setDistancePerPulse`.

        :returns: The current rate of the encoder.
        """
        return hal.getEncoderRate(self.encoder)

    def setMinRate(self, minRate: float) -> None:
        """Set the minimum rate of the device before the hardware reports it
        stopped.

        :param minRate: The minimum rate. The units are in distance per
            second as scaled by the value from :func:`setDistancePerPulse`.
        """
        hal.setEncoderMinRate(self.encoder, minRate)

    def setDistancePerPulse(self, distancePerPulse: float) -> None:
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
        hal.setEncoderDistancePerPulse(self.encoder, distancePerPulse)

    def getDistancePerPulse(self) -> float:
        """ 
        Get the distance per pulse for this encoder.

        :returns: The scale factor that will be used to convert pulses to useful units.
        """
        return hal.getEncoderDistancePerPulse(self.encoder)

    def setReverseDirection(self, reverseDirection: bool) -> None:
        """Set the direction sensing for this encoder. This sets the direction
        sensing on the encoder so that it could count in the correct software
        direction regardless of the mounting.

        :param reverseDirection: True if the encoder direction should be
            reversed
        """
        hal.setEncoderReverseDirection(self.encoder, reverseDirection)

    def setSamplesToAverage(self, samplesToAverage: int) -> None:
        """Set the Samples to Average which specifies the number of samples
        of the timer to average when calculating the period. Perform averaging
        to account for mechanical imperfections or as oversampling to increase
        resolution.

        TODO: Should this raise an exception, so that the user has to
        deal with giving an incorrect value?

        :param samplesToAverage: The number of samples to average from 1 to
            127.
        """
        hal.setEncoderSamplesToAverage(self.encoder, samplesToAverage)

    def getSamplesToAverage(self) -> int:
        """Get the Samples to Average which specifies the number of samples
        of the timer to average when calculating the period. Perform averaging
        to account for mechanical imperfections or as oversampling to increase
        resolution.

        :returns: The number of samples being averaged (from 1 to 127)
        """
        return hal.getEncoderSamplesToAverage(self.encoder)

    def setPIDSourceType(self, pidSource: PIDSourceType) -> None:
        """Set which parameter of the encoder you are using as a process
        control variable. The encoder class supports the rate and distance
        parameters.

        :param pidSource: An enum to select the parameter.
        """
        if pidSource not in (
            self.PIDSourceType.kDisplacement,
            self.PIDSourceType.kRate,
        ):
            raise ValueError("Must be kRate or kDisplacement")
        self.pidSource = pidSource

    def getPIDSourceType(self) -> PIDSourceType:
        return self.pidSource

    def pidGet(self) -> float:
        """Implement the PIDSource interface.

         :returns: The current value of the selected source parameter.
        """
        if self.pidSource == self.PIDSourceType.kDisplacement:
            return self.getDistance()
        elif self.pidSource == self.PIDSourceType.kRate:
            return self.getRate()
        else:
            return 0.0

    def setIndexSource(
        self,
        source: Union[int, DigitalInput],
        indexing_type: IndexingType = IndexingType.kResetOnRisingEdge,
    ) -> None:
        """
        Set the index source for the encoder. When this source rises, the encoder count automatically resets.

        :param source: Either an initialized DigitalSource or a DIO channel number
        :param indexing_type: The state that will cause the encoder to reset
        """
        if hasattr(source, "getPortHandleForRouting"):
            self.indexSource = source
        else:
            self.indexSource = DigitalInput(source)

        hal.setEncoderIndexSource(
            self.encoder,
            self.indexSource.getPortHandleForRouting(),
            self.indexSource.getAnalogTriggerTypeForRouting(),
            indexing_type,
        )

    def initSendable(self, builder: SendableBuilder) -> None:
        if self.encodingType == self.EncodingType.k4X:
            builder.setSmartDashboardType("Quadrature Encoder")
        else:
            builder.setSmartDashboardType("Encoder")

        builder.addDoubleProperty("Speed", self.getRate, None)
        builder.addDoubleProperty("Distance", self.getDistance, None)
        builder.addDoubleProperty("Distance per Tick", self.getDistancePerPulse, None)
