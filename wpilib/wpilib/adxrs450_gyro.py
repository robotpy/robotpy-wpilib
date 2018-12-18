# validated: 2018-12-14 DS dcbf02a1ecfc edu/wpi/first/wpilibj/ADXRS450_Gyro.java
# ----------------------------------------------------------------------------
# Copyright (c) 2015-2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Optional

import hal

from .driverstation import DriverStation
from .gyrobase import GyroBase
from .spi import SPI
from .timer import Timer

__all__ = ["ADXRS450_Gyro"]


class ADXRS450_Gyro(GyroBase):
    """
    Use a rate gyro to return the robots heading relative to a starting position.
    The Gyro class tracks the robots heading based on the starting position. As
    the robot rotates the new heading is computed by integrating the rate of
    rotation returned by the sensor. When the class is instantiated, it does a
    short calibration routine where it samples the gyro while at rest to
    determine the default offset. This is subtracted from each sample to
    determine the heading.

    This class is for the digital ADXRS450 gyro sensor that connects via SPI.
    """

    kSamplePeriod = 0.0005
    kCalibrationSampleTime = 5.0
    kDegreePerSecondPerLSB = 0.0125

    kRateRegister = 0x00
    kTemRegister = 0x02
    kLoCSTRegister = 0x04
    kHiCSTRegister = 0x06
    kQuadRegister = 0x08
    kFaultRegister = 0x0A
    kPIDRegister = 0x0C
    kSNHighRegister = 0x0E
    kSNLowRegister = 0x10

    def __init__(self, port: Optional[SPI.Port] = None) -> None:
        """
            Constructor.

            :param port: The SPI port that the gyro is connected to
        """
        super().__init__()

        if port is None:
            port = SPI.Port.kOnboardCS0

        simPort = None
        if hal.HALIsSimulation():
            from hal_impl.spi_helpers import ADXRS450_Gyro_Sim

            simPort = ADXRS450_Gyro_Sim(self)

        self.spi = SPI(port, simPort=simPort)

        self.spi.setClockRate(3000000)
        self.spi.setMSBFirst()
        self.spi.setSampleDataOnLeadingEdge()
        self.spi.setClockActiveHigh()
        self.spi.setChipSelectActiveLow()

        # Validate the part ID
        if (self._readRegister(self.kPIDRegister) & 0xFF00) != 0x5200:
            self.spi.close()
            self.spi = None
            DriverStation.reportError(
                "could not find ADXRS450 gyro on SPI port %s" % port, False
            )
            return

        # python-specific: make this easier to simulate
        if hal.isSimulation():
            self.spi.initAccumulator(
                self.kSamplePeriod, 0x20000000, 4, 0x0, 0x0, 0, 32, True, True
            )
        else:
            self.spi.initAccumulator(
                self.kSamplePeriod,
                0x20000000,
                4,
                0x0C00000E,
                0x04000000,
                10,
                16,
                True,
                True,
            )

        self.calibrate()

        hal.report(hal.UsageReporting.kResourceType_ADXRS450, port)
        self.setName("ADXRS450_Gyro", port)

    def isConnected(self) -> bool:
        return self.spi is not None

    def calibrate(self) -> None:
        """Calibrate the gyro by running for a number of samples and computing the
        center value. Then use the center value as the Accumulator center value for
        subsequent measurements.

        It's important to make sure that the robot is not moving while the centering
        calculations are in progress, this is typically done when the robot is first
        turned on while it's sitting at rest before the competition starts.

        .. note:: Usually you don't need to call this, as it's called when the
                  object is first created. If you do, it will freeze your robot
                  for 5 seconds
        """

        if self.spi is None:
            return

        if not hal.HALIsSimulation():
            Timer.delay(0.1)

        self.spi.setAccumulatorIntegratedCenter(0)
        self.spi.resetAccumulator()

        if not hal.HALIsSimulation():
            Timer.delay(self.kCalibrationSampleTime)

        self.spi.setAccumulatorIntegratedCenter(
            int(self.spi.getAccumulatorIntegratedAverage())
        )
        self.spi.resetAccumulator()

    def _calcParity(self, v: int) -> bool:
        parity = False
        while v != 0:
            parity = not parity
            v = v & (v - 1)
        return parity

    def _readRegister(self, reg: int) -> int:
        cmdhi = 0x8000 | (reg << 1)
        parity = self._calcParity(cmdhi)

        data = [cmdhi >> 8, cmdhi & 0xFF, 0, 0 if parity else 1]

        self.spi.write(data)
        data = self.spi.read(False, 4)

        if (data[0] & 0xE0) == 0:
            return 0  # error, return 0

        val = int.from_bytes(data[:4], byteorder="big")
        return (val >> 5) & 0xFFFF

    def reset(self) -> None:
        """
        Reset the gyro.
        
        Resets the gyro to a heading of zero. This can be used if
        there is significant drift in the gyro and it needs to be recalibrated
        after it has been running.
        """
        if self.spi is not None:
            self.spi.resetAccumulator()

    def close(self) -> None:
        """Delete (free) the spi port used for the gyro and stop accumulating."""
        super().close()
        if self.spi is not None:
            self.spi.close()
            self.spi = None

    def getAngle(self) -> float:
        """
        Return the actual angle in degrees that the robot is currently facing.

        The angle is based on the current accumulator value corrected by the
        oversampling rate, the gyro type and the A/D calibration values. The angle
        is continuous, that is it will continue from 360 to 361 degrees. This
        allows algorithms that wouldn't want to see a discontinuity in the gyro
        output as it sweeps past from 360 to 0 on the second time around.

        :returns: the current heading of the robot in degrees. This heading is based
                  on integration of the returned rate from the gyro.
        """
        if self.spi is None:
            return 0.0
        return (
            self.spi.getAccumulatorValue()
            * self.kDegreePerSecondPerLSB
            * self.kSamplePeriod
        )

    def getRate(self) -> float:
        """Return the rate of rotation of the gyro

        The rate is based on the most recent reading of the gyro value

        :returns: the current rate in degrees per second
        """
        if self.spi is None:
            return 0.0
        else:
            return (
                self.spi.getAccumulatorIntegratedValue() * self.kDegreePerSecondPerLSB
            )
