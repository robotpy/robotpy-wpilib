# validated: 2016-12-25 JW e44a6e227a89 athena/java/edu/wpi/first/wpilibj/DigitalGlitchFilter.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2015. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in $(WIND_BASE)/WPILib.
#----------------------------------------------------------------------------

import hal
import threading

from .digitalsource import DigitalSource
from .encoder import Encoder
from .counter import Counter
from .sensorbase import SensorBase

__all__ = ['DigitalGlitchFilter']

class DigitalGlitchFilter(SensorBase):
    '''
    Class to enable glitch filtering on a set of digital inputs.
    This class will manage adding and removing digital inputs from a FPGA glitch
    filter. The filter lets the user configure the time that an input must remain
    high or low before it is classified as high or low.
    '''
    
    mutex = threading.Lock()
    filterAllocated = [False]*3
    
    def __init__(self):
        self.channelIndex = -1
        with self.mutex:
            for i, v in enumerate(self.filterAllocated):
                if not v:
                    self.channelIndex = i
                    self.filterAllocated[i] = True
                    hal.report(hal.UsageReporting.kResourceType_DigitalFilter,
                               self.channelIndex, 0)
                    break
            else:
                raise ValueError("No more filters available")
    
    def free(self):
        if self.channelIndex >= 0:
            with self.mutex:
                self.filterAllocated[self.channelIndex] = False
            
            self.channelIndex = -1
    
    @staticmethod
    def _setFilter(input, channelIndex):
        if input is not None: # Counter might have just one input
            # analog triggers are not supported for DigitalGlitchFilter
            if input.isAnalogTrigger():
                raise ValueError("Analog Triggers are not supported for DigitalGlitchFilters")
            hal.setFilterSelect(input.getPortHandleForRouting(), channelIndex)
            
            selected = hal.getFilterSelect(input.getPortHandleForRouting())
            if selected != channelIndex:
                raise ValueError('setFilterSelect(%s) failed -> %s' % (channelIndex, selected))
    
    def add(self, input):
        '''
        Assigns the :class:`.DigitalSource`, :class:`.Encoder`, or
        :class:`.Counter` to this glitch filter.
        
        :param input: The object to add
        '''
        if isinstance(input, DigitalSource):
            DigitalGlitchFilter._setFilter(input, self.channelIndex + 1)
        elif isinstance(input, Encoder):
            DigitalGlitchFilter._setFilter(input.aSource, self.channelIndex + 1)
            DigitalGlitchFilter._setFilter(input.bSource, self.channelIndex + 1)
        elif isinstance(input, Counter):
            DigitalGlitchFilter._setFilter(input.upSource, self.channelIndex + 1)
            DigitalGlitchFilter._setFilter(input.downSource, self.channelIndex + 1)
        else:
            raise ValueError("Cannot add %s to glitch filter" % input)
        
    def remove(self, input):
        '''
        Removes this filter from the given input object
        '''
        
        if isinstance(input, DigitalSource):
            DigitalGlitchFilter._setFilter(input, 0)
        elif isinstance(input, Encoder):
            DigitalGlitchFilter._setFilter(input.aSource, 0)
            DigitalGlitchFilter._setFilter(input.bSource, 0)
        elif isinstance(input, Counter):
            DigitalGlitchFilter._setFilter(input.upSource, 0)
            DigitalGlitchFilter._setFilter(input.downSource, 0)
        else:
            raise ValueError("Cannot remove %s from glitch filter" % input)
        
    def setPeriodCycles(self, fpga_cycles):
        '''
        Sets the number of FPGA cycles that the input must hold steady to pass
        through this glitch filter.
        
        :param fpga_cycles: The number of FPGA cycles.
        '''
        hal.setFilterPeriod(self.channelIndex, fpga_cycles)
        
    def setPeriodNanoSeconds(self, nanoseconds):
        '''
        Sets the number of nanoseconds that the input must hold steady to pass
        through this glitch filter.
        
        :param nanoseconds: The number of nanoseconds.
        '''
        fpga_cycles = int(nanoseconds * self.kSystemClockTicksPerMicrosecond / 4 / 1000)
        self.setPeriodCycles(fpga_cycles)
    
    def getPeriodCycles(self):
        '''
        Gets the number of FPGA cycles that the input must hold steady to pass
        through this glitch filter.
       
        :returns: The number of cycles.
        '''
        return hal.getFilterPeriod(self.channelIndex)
    
    def getPeriodNanoSeconds(self):
        '''
        Gets the number of nanoseconds that the input must hold steady to pass
        through this glitch filter.
       
        :returns: The number of nanoseconds.
        '''
        fpga_cycles = self.getPeriodCycles()
        return fpga_cycles * 1000 / (self.kSystemClockTicksPerMicrosecond / 4)
