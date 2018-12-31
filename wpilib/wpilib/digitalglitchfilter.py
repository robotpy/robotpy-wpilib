# validated: 2018-09-09 EN d54c2665dc54 edu/wpi/first/wpilibj/DigitalGlitchFilter.java
# ----------------------------------------------------------------------------
# Copyright (c) 2015-2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in $(WIND_BASE)/WPILib.
# ----------------------------------------------------------------------------
from typing import Union

import hal
import threading

from .digitalsource import DigitalSource
from .encoder import Encoder
from .counter import Counter
from .sendablebuilder import SendableBuilder
from .sensorutil import SensorUtil
from .sendablebase import SendableBase

__all__ = ["DigitalGlitchFilter"]


class DigitalGlitchFilter(SendableBase):
    """
    Class to enable glitch filtering on a set of digital inputs.
    This class will manage adding and removing digital inputs from a FPGA glitch
    filter. The filter lets the user configure the time that an input must remain
    high or low before it is classified as high or low.
    """

    mutex = threading.Lock()
    filterAllocated = [False] * 3

    def __init__(self) -> None:
        super().__init__()
        self.channelIndex = -1
        with self.mutex:
            for i, v in enumerate(self.filterAllocated):
                if not v:
                    self.channelIndex = i
                    self.filterAllocated[i] = True
                    hal.report(
                        hal.UsageReporting.kResourceType_DigitalGlitchFilter,
                        self.channelIndex,
                        0,
                    )
                    self.setName("DigitalGlitchFilter", i)
                    break
            else:
                raise ValueError("No more filters available")

    def close(self) -> None:
        super().close()
        if self.channelIndex >= 0:
            with self.mutex:
                self.filterAllocated[self.channelIndex] = False

            self.channelIndex = -1

    @staticmethod
    def _setFilter(input: DigitalSource, channelIndex: int) -> None:
        if input is not None:  # Counter might have just one input
            # analog triggers are not supported for DigitalGlitchFilter
            if input.isAnalogTrigger():
                raise ValueError(
                    "Analog Triggers are not supported for DigitalGlitchFilters"
                )
            hal.setFilterSelect(input.getPortHandleForRouting(), channelIndex)

            selected = hal.getFilterSelect(input.getPortHandleForRouting())
            if selected != channelIndex:
                raise ValueError(
                    "setFilterSelect(%s) failed -> %s" % (channelIndex, selected)
                )

    def add(self, input: Union[DigitalSource, Encoder, Counter]) -> None:
        """
        Assigns the :class:`.DigitalSource`, :class:`.Encoder`, or
        :class:`counter.Counter` to this glitch filter.

        :param input: The object to add
        """
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

    def remove(self, input: Union[DigitalSource, Encoder, Counter]) -> None:
        """
        Removes this filter from the given input object
        """

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

    def setPeriodCycles(self, fpga_cycles: int) -> None:
        """
        Sets the number of FPGA cycles that the input must hold steady to pass
        through this glitch filter.

        :param fpga_cycles: The number of FPGA cycles.
        """
        hal.setFilterPeriod(self.channelIndex, fpga_cycles)

    def setPeriodNanoSeconds(self, nanoseconds: float) -> None:
        """
        Sets the number of nanoseconds that the input must hold steady to pass
        through this glitch filter.

        :param nanoseconds: The number of nanoseconds.
        """
        fpga_cycles = int(
            nanoseconds * SensorUtil.kSystemClockTicksPerMicrosecond / 4 / 1000
        )
        self.setPeriodCycles(fpga_cycles)

    def getPeriodCycles(self) -> int:
        """
        Gets the number of FPGA cycles that the input must hold steady to pass
        through this glitch filter.

        :returns: The number of cycles.
        """
        return hal.getFilterPeriod(self.channelIndex)

    def getPeriodNanoSeconds(self) -> float:
        """
        Gets the number of nanoseconds that the input must hold steady to pass
        through this glitch filter.

        :returns: The number of nanoseconds.
        """
        fpga_cycles = self.getPeriodCycles()
        return fpga_cycles * 1000 / (SensorUtil.kSystemClockTicksPerMicrosecond / 4)

    def initSendable(self, builder: SendableBuilder) -> None:
        pass
