# validated: 2016-12-31 JW 8f67f2c24cb9 athena/java/edu/wpi/first/wpilibj/ADXRS450_Gyro.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2015. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .driverstation import DriverStation
from .gyrobase import GyroBase
from .livewindow import LiveWindow
from .spi import SPI
from .timer import Timer
    

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
    
    kSamplePeriod = 0.001
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

    def __init__(self, port=None):
        """
            Constructor.
        
            :param port: The SPI port that the gyro is connected to
            :type port: :class:`.SPI.Port`
        """
        
        if port is None:
            port = SPI.Port.kOnboardCS0
        
        simPort = None
        if hal.HALIsSimulation():
            from hal_impl.spi_helpers import ADXRS450_Gyro_Sim
            simPort = ADXRS450_Gyro_Sim(self)
        
        self.spi = SPI(port, simPort=simPort)
        self.spi.setClockRate(3000000)
        self.spi.setMSBFirst()
        self.spi.setSampleDataOnRising()
        self.spi.setClockActiveHigh()
        self.spi.setChipSelectActiveLow()

        # Validate the part ID
        if (self._readRegister(self.kPIDRegister) & 0xff00) != 0x5200:
            self.spi.free()
            self.spi = None
            DriverStation.reportError("could not find ADXRS450 gyro on SPI port %s" % port, False)
            return
        
        self.spi.initAccumulator(self.kSamplePeriod, 0x20000000, 4, 0x0c00000e, 0x04000000,
            10, 16, True, True)
        
        self.calibrate()
        
        hal.report(hal.UsageReporting.kResourceType_ADXRS450, port)
        LiveWindow.addSensor("ADXRS450_Gyro", port, self)

    def calibrate(self):
        if self.spi is None:
            return
        
        if not hal.HALIsSimulation():
            Timer.delay(0.1)

        self.spi.setAccumulatorCenter(0)
        self.spi.resetAccumulator()
        
        if not hal.HALIsSimulation():
            Timer.delay(self.kCalibrationSampleTime)
        
        self.spi.setAccumulatorCenter(int(self.spi.getAccumulatorAverage()))
        self.spi.resetAccumulator()

    def _calcParity(self, v):
        parity = False
        while v != 0:
            parity = not parity
            v = v & (v - 1)
        return parity
    
    def _readRegister(self, reg):
        cmdhi = 0x8000 | (reg << 1)
        parity = self._calcParity(cmdhi)
    
        data = [cmdhi >> 8,
                cmdhi & 0xff,
                0,
                0 if parity else 1] 
    
        self.spi.write(data)
        data = self.spi.read(False, 4)
    
        if (data[0] & 0xe0) == 0:
            return 0  # error, return 0
        
        val = int.from_bytes(data[:4], byteorder='big')
        return (val >> 5) & 0xffff
    
    def reset(self):
        self.spi.resetAccumulator()
        
    def free(self):
        """Delete (free) the spi port used for the gyro and stop accumulating."""
        if self.spi is not None:
            self.spi.free()
            self.spi = None
    
    def getAngle(self):
        if self.spi is None:
            return 0.0
        return self.spi.getAccumulatorValue() * self.kDegreePerSecondPerLSB * self.kSamplePeriod

    def getRate(self):
        if self.spi is None:
            return 0.0
        else:
            return self.spi.getAccumulatorLastValue() * self.kDegreePerSecondPerLSB

