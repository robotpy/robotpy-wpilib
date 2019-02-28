# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/AnalogInput.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal
import weakref

from .accumulatorresult import AccumulatorResult
from .interfaces import PIDSource
from .livewindow import LiveWindow
from .resource import Resource
from .sendablebase import SendableBase
from .sensorutil import SensorUtil
from .sendablebuilder import SendableBuilder
from .timer import Timer

__all__ = ["AnalogInput"]


def _freeAnalogInput(port: hal.AnalogInputHandle) -> None:
    hal.freeAnalogInputPort(port)


class AnalogInput(SendableBase):
    """Analog input

    Each analog channel is read from hardware as a 12-bit number representing
    0V to 5V.

    Connected to each analog channel is an averaging and oversampling engine.
    This engine accumulates the specified (by :func:`setAverageBits` and
    :func:`setOversampleBits`) number of samples before returning a new value.
    This is not a sliding window average. The only difference between the
    oversampled samples and the averaged samples is that the oversampled
    samples are simply accumulated effectively increasing the resolution,
    while the averaged samples are divided by the number of samples to retain
    the resolution, but get more stable values.
    """

    kAccumulatorSlot = 1
    kAccumulatorChannels = (0, 1)
    channels = Resource(SensorUtil.kAnalogInputChannels)

    PIDSourceType = PIDSource.PIDSourceType

    def __init__(self, channel: int) -> None:
        """Construct an analog channel.

        :param channel: The channel number to represent. 0-3 are on-board 4-7 are on the MXP port.
        """

        super().__init__()
        hal.checkAnalogInputChannel(channel)

        self.channel = channel
        self.accumulatorOffset = 0
        self.pidSource = self.PIDSourceType.kDisplacement

        port = hal.getPort(channel)
        self.port = hal.initializeAnalogInputPort(port)

        hal.report(hal.UsageReporting.kResourceType_AnalogChannel, channel)
        self.setName("AnalogInput", self.channel)

        self.__finalizer = weakref.finalize(self, _freeAnalogInput, self.port)

    def close(self) -> None:
        """ Channel destructor """
        super().close()
        if self.channel is None:
            return
        AnalogInput.channels.free(self.channel)
        self.__finalizer()
        self.channel = None
        self.accumulatorOffset = 0
        self.port = None

    def getValue(self) -> int:
        """Get a sample straight from this channel. The sample is a 12-bit
        value representing the 0V to 5V range of the A/D converter. The units
        are in A/D converter codes. Use :func:`getVoltage` to get the analog
        value in calibrated units.

        :returns: A sample straight from this channel.
        """
        return hal.getAnalogValue(self.port)

    def getAverageValue(self) -> float:
        """Get a sample from the output of the oversample and average engine
        for this channel. The sample is 12-bit + the bits configured in
        :func:`setOversampleBits`. The value configured in
        :func:`setAverageBits` will cause this value to be averaged 2**bits
        number of samples. This is not a sliding window. The sample will not
        change until 2^(OversampleBits + AverageBits) samples have been
        acquired from this channel. Use :func:`getAverageVoltage` to get the
        analog value in calibrated units.

        :returns: A sample from the oversample and average engine for this
            channel.
        """
        return hal.getAnalogAverageValue(self.port)

    def getVoltage(self) -> float:
        """Get a scaled sample straight from this channel. The value is scaled
        to units of Volts using the calibrated scaling data from
        :func:`getLSBWeight` and :func:`getOffset`.

        :returns: A scaled sample straight from this channel.
        """
        return hal.getAnalogVoltage(self.port)

    def getAverageVoltage(self) -> float:
        """Get a scaled sample from the output of the oversample and average
        engine for this channel. The value is scaled to units of Volts using
        the calibrated scaling data from :func:`getLSBWeight` and
        :func:`getOffset`. Using oversampling will cause this value to be
        higher resolution, but it will update more slowly. Using averaging
        will cause this value to be more stable, but it will update more
        slowly.

        :returns: A scaled sample from the output of the oversample and average
            engine for this channel.
        """
        return hal.getAnalogAverageVoltage(self.port)

    def getLSBWeight(self) -> float:
        """Get the factory scaling least significant bit weight constant. The
        least significant bit weight constant for the channel that was
        calibrated in manufacturing and stored in an eeprom.

        Volts = ((LSB_Weight * 1e-9) * raw) - (Offset * 1e-9)

        :returns: Least significant bit weight.
        """
        return hal.getAnalogLSBWeight(self.port)

    def getOffset(self) -> int:
        """Get the factory scaling offset constant. The offset constant for the
        channel that was calibrated in manufacturing and stored in an eeprom.

        Volts = ((LSB_Weight * 1e-9) * raw) - (Offset * 1e-9)

        :returns: Offset constant.
        """
        return hal.getAnalogOffset(self.port)

    def getChannel(self) -> int:
        """Get the channel number.

        :returns: The channel number.
        """
        return self.channel

    def setAverageBits(self, bits: int) -> None:
        """Set the number of averaging bits. This sets the number of
        averaging bits.  The actual number of averaged samples is 2^bits.
        The averaging is done automatically in the FPGA.

        :param bits: The number of averaging bits.
        """
        hal.setAnalogAverageBits(self.port, bits)

    def getAverageBits(self) -> int:
        """Get the number of averaging bits. This gets the number of averaging
        bits from the FPGA. The actual number of averaged samples is 2^bits.
        The averaging is done automatically in the FPGA.

        :returns: The number of averaging bits.
        """
        return hal.getAnalogAverageBits(self.port)

    def setOversampleBits(self, bits: int) -> None:
        """Set the number of oversample bits. This sets the number of
        oversample bits. The actual number of oversampled values is 2^bits.
        The oversampling is done automatically in the FPGA.

        :param bits: The number of oversample bits.
        """
        hal.setAnalogOversampleBits(self.port, bits)

    def getOversampleBits(self) -> int:
        """Get the number of oversample bits. This gets the number of
        oversample bits from the FPGA. The actual number of oversampled values
        is 2^bits.  The oversampling is done automatically in the FPGA.

        :returns: The number of oversample bits.
        """
        return hal.getAnalogOversampleBits(self.port)

    def initAccumulator(self) -> None:
        """Initialize the accumulator.
        """
        if not self.isAccumulatorChannel():
            raise IndexError(
                "Accumulators are only available on slot %d on channels %s"
                % (
                    AnalogInput.kAccumulatorSlot,
                    ",".join(str(c) for c in AnalogInput.kAccumulatorChannels),
                )
            )
        self.accumulatorOffset = 0
        hal.initAccumulator(self.port)

    def setAccumulatorInitialValue(self, initialValue: float) -> None:
        """Set an initial value for the accumulator.

        This will be added to all values returned to the user.

        :param initialValue:
            The value that the accumulator should start from when reset.
        """
        self.accumulatorOffset = initialValue

    def resetAccumulator(self) -> None:
        """Resets the accumulator to the initial value.
        """
        hal.resetAccumulator(self.port)

        # Wait until the next sample, so the next call to getAccumulator*()
        # won't have old values.
        sampleTime = 1.0 / AnalogInput.getGlobalSampleRate()
        overSamples = 1 << self.getOversampleBits()
        averageSamples = 1 << self.getAverageBits()
        if not hal.HALIsSimulation():
            Timer.delay(sampleTime * overSamples * averageSamples)

    def setAccumulatorCenter(self, center: int) -> None:
        """Set the center value of the accumulator.

        The center value is subtracted from each A/D value before it is added
        to the accumulator. This is used for the center value of devices like
        gyros and accelerometers to make integration work and to take the
        device offset into account when integrating.

        This center value is based on the output of the oversampled and
        averaged source from channel 1. Because of this, any non-zero
        oversample bits will affect the size of the value for this field.
        """
        hal.setAccumulatorCenter(self.port, center)

    def setAccumulatorDeadband(self, deadband: int) -> None:
        """Set the accumulator's deadband.
        """
        hal.setAccumulatorDeadband(self.port, deadband)

    def getAccumulatorValue(self) -> float:
        """Read the accumulated value.

        Read the value that has been accumulating. The accumulator
        is attached after the oversample and average engine.

        :returns: The 64-bit value accumulated since the last call to :func:`resetAccumulator`.
        """
        return hal.getAccumulatorValue(self.port) + self.accumulatorOffset

    def getAccumulatorCount(self) -> float:
        """Read the number of accumulated values.

        Read the count of the accumulated values since the last call to
        :func:`resetAccumulator`.

        :returns: The number of times samples from the channel were
            accumulated.
        """
        return hal.getAccumulatorCount(self.port)

    def getAccumulatorOutput(self) -> AccumulatorResult:
        """Read the accumulated value and the number of accumulated values
        atomically.

        This function reads the value and count from the FPGA atomically. This
        can be used for averaging.
        """
        if not self.isAccumulatorChannel():
            raise IndexError("Channel %d is not an accumulator channel." % self.channel)
        (value, count) = hal.getAccumulatorOutput(self.port)

        return AccumulatorResult(value + self.accumulatorOffset, count)

    def isAccumulatorChannel(self) -> bool:
        """Is the channel attached to an accumulator.

        :returns: The analog channel is attached to an accumulator.
        """
        return self.channel in AnalogInput.kAccumulatorChannels

    @staticmethod
    def setGlobalSampleRate(samplesPerSecond: float) -> None:
        """Set the sample rate per channel.

        This is a global setting for all channels.
        The maximum rate is 500kS/s divided by the number of channels in use.
        This is 62500 samples/s per channel if all 8 channels are used.

        :param samplesPerSecond: The number of samples per second.
        """
        hal.setAnalogSampleRate(float(samplesPerSecond))

    @staticmethod
    def getGlobalSampleRate() -> float:
        """Get the current sample rate.

        This assumes one entry in the scan list. This is a global setting for
        all channels.

        :returns: Sample rate.
        """
        return hal.getAnalogSampleRate()

    def setPIDSourceType(self, pidSource: PIDSourceType) -> None:
        """:see: :meth:`.PIDSource.setPIDSourceType`"""
        self.pidSource = pidSource

    def getPIDSourceType(self) -> PIDSourceType:
        """:see: :meth:`.PIDSource.getPIDSourceType`"""
        return self.pidSource

    def pidGet(self) -> float:
        """Get the average voltage for use with PIDController

        :returns: the average voltage
        """
        return self.getAverageVoltage()

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Analog Input")
        builder.addDoubleProperty("Value", self.getAverageVoltage, None)
