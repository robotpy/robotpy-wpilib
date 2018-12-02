import math
import pytest
import random
from unittest.mock import MagicMock

# Filter constants taken from Java WPILIB
# allwpilib/blob/master/wpilibjIntegrationTests/src/main/java/edu/wpi/first/wpilibj/test/TestBench.java

kStdDev = 10.0
kFilterStep = 0.005
kFilterTime = 2.0
kSinglePoleIIRTimeConstant = 0.015915
kSinglePoleIIRExpectedOutput = -3.2172003
kHighPassTimeConstant = 0.006631
kHighPassExpectedOutput = 10.074717
kMovAvgTaps = 6
kMovAvgExpectedOutput = -10.191644


class FilterSource:
    def __init__(self):
        self.t = [t * kFilterStep for t in range(int(kFilterTime / kFilterStep))]
        self.pid_idx = 0

    def reset(self):
        self.pid_idx = 0

    def getPIDSourceType(self):
        assert False

    def pidGet(self):
        self.pid_idx += 1
        return self.pid_data[self.pid_idx - 1]


class OutputSource(FilterSource):
    def __init__(self):
        super().__init__()
        self.pid_data = [
            100.0 * math.sin(2.0 * math.pi * t) + 20.0 * math.cos(50.0 * math.pi * t)
            for t in self.t
        ]


class NoiseSource(FilterSource):
    def __init__(self):
        super().__init__()
        self.clean_data = [100.0 * math.sin(2.0 * math.pi * t) for t in self.t]
        self.pid_data = [
            c + random.normalvariate(0.0, kStdDev) for c in self.clean_data
        ]


def test_noise_reduce(wpilib):
    source = NoiseSource()

    spiir = wpilib.LinearDigitalFilter.singlePoleIIR(
        source, kSinglePoleIIRTimeConstant, kFilterStep
    )
    movavg = wpilib.LinearDigitalFilter.movingAverage(source, kMovAvgTaps)
    filters = {"Single pole IIR": spiir, "Moving average": movavg}

    for name, flt in filters.items():
        noiseGenError = 0.0
        filterError = 0.0
        source.reset()
        for idx in range(int(kFilterTime / kFilterStep)):
            filterError += abs(spiir.pidGet() - source.clean_data[idx])
            noiseGenError += abs(source.pid_data[idx] - source.clean_data[idx])
        assert noiseGenError > filterError, (
            "%s should have reduced noise accumulation from %f but failed. The filter error was %f"
            % (name, noiseGenError, filterError)
        )


def test_output(wpilib):
    source = OutputSource()

    spiir = wpilib.LinearDigitalFilter.singlePoleIIR(
        source, kSinglePoleIIRTimeConstant, kFilterStep
    )
    highpass = wpilib.LinearDigitalFilter.highPass(
        source, kHighPassTimeConstant, kFilterStep
    )
    movavg = wpilib.LinearDigitalFilter.movingAverage(source, kMovAvgTaps)
    filters = {
        "Single pole IIR": (spiir, kSinglePoleIIRExpectedOutput),
        "High pass": (highpass, kHighPassExpectedOutput),
        "Moving average": (movavg, kMovAvgExpectedOutput),
    }

    for name, (flt, expected) in filters.items():
        output = 0.0
        source.reset()
        for idx in range(int(kFilterTime / kFilterStep)):
            output = flt.pidGet()
        assert abs(output - expected) > 0.00005, "%s output was incorrect" % name


def test_invalid_taps(wpilib):
    source = OutputSource()

    with pytest.raises(ValueError):
        movavg = wpilib.LinearDigitalFilter.movingAverage(source, 0)
    with pytest.raises(ValueError):
        movavg = wpilib.LinearDigitalFilter.movingAverage(source, -1)


def test_get(wpilib):
    source = OutputSource()
    hp = wpilib.LinearDigitalFilter.highPass(source, kHighPassTimeConstant, kFilterStep)

    for i in range(10):
        hp.pidGet()

    # Repeated calls to get() should not result in changes to inputs and outputs
    prev_in = hp.inputs[-1]
    prev_out = hp.outputs[-1]
    assert hp.get() == hp.get()
    assert prev_in == hp.inputs[-1]
    assert prev_out == hp.outputs[-1]
    hp.pidGet()
    assert prev_in != hp.inputs[-1]
    assert prev_out != hp.outputs[-1]


def test_reset(wpilib):
    source = OutputSource()
    movavg = wpilib.LinearDigitalFilter.movingAverage(source, kMovAvgTaps)

    for i in range(10):
        movavg.pidGet()

    movavg.reset()

    assert len(movavg.inputs) == 0
    assert len(movavg.outputs) == 0
