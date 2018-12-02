# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from collections import namedtuple

__all__ = ["AccumulatorResult"]

AccumulatorResult = namedtuple("AccumulatorResult", ["value", "count"])

AccumulatorResult.__doc__ = "Structure for holding the values stored in an accumulator."
AccumulatorResult.value.__doc__ = "The total value accumulated."
AccumulatorResult.count.__doc__ = "The number of sample value was accumulated over."
