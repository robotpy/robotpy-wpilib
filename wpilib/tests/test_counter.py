import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def counter_table(networktables):
    return networktables.NetworkTables.getTable("dacounter")


def check_init(
    hal_data, mode, up, down, up_edge, down_edge, trigger_up=False, trigger_down=False
):
    assert hal_data["counter"][0]["initialized"]
    assert hal_data["counter"][0]["mode"] == mode
    assert hal_data["counter"][0]["up_source_channel"] == up
    assert hal_data["counter"][0]["down_source_channel"] == down
    assert hal_data["counter"][0]["up_source_trigger"] == trigger_up
    assert hal_data["counter"][0]["down_source_trigger"] == trigger_down
    assert hal_data["counter"][0]["up_rising_edge"] == up_edge[0]
    assert hal_data["counter"][0]["up_falling_edge"] == up_edge[1]
    assert hal_data["counter"][0]["down_rising_edge"] == down_edge[0]
    assert hal_data["counter"][0]["down_falling_edge"] == down_edge[1]


def test_counter_init_1(wpilib, hal_data):
    ctr = wpilib.Counter()
    check_init(
        hal_data, wpilib.Counter.Mode.kTwoPulse, 0, 0, (False, False), (False, False)
    )


def test_counter_init_2(wpilib, hal_data):
    di = wpilib.DigitalInput(5)
    ctr = wpilib.Counter(di)
    check_init(
        hal_data, wpilib.Counter.Mode.kTwoPulse, 5, 0, (True, False), (False, False)
    )


def test_counter_init_3(wpilib, hal_data):
    ctr = wpilib.Counter(6)
    check_init(
        hal_data, wpilib.Counter.Mode.kTwoPulse, 6, 0, (True, False), (False, False)
    )
    assert hal_data["dio"][6]["initialized"] == True
    assert hal_data["dio"][6]["is_input"] == True


def test_counter_init_4(wpilib, hal_data):
    us = wpilib.DigitalInput(3)
    ds = wpilib.DigitalInput(4)
    ctr = wpilib.Counter(wpilib.Counter.EncodingType.k1X, us, ds, True)
    check_init(
        hal_data,
        wpilib.Counter.Mode.kExternalDirection,
        3,
        4,
        (True, False),
        (True, True),
    )


def test_counter_init_5(wpilib, hal_data):
    at = wpilib.AnalogTrigger(2)
    ctr = wpilib.Counter(at)
    # Analog triggers get their channel ids from their index, not their analog port.
    check_init(
        hal_data,
        wpilib.Counter.Mode.kTwoPulse,
        0,
        0,
        (True, False),
        (False, False),
        True,
    )


def test_counter_set_up_channel(wpilib, hal_data):
    ctr = wpilib.Counter()
    ctr.setUpSource(2)
    check_init(hal_data, 0, 2, 0, (True, False), (False, False))
    assert hal_data["dio"][2]["initialized"] == True
    assert hal_data["dio"][2]["is_input"] == True


def test_counter_set_up_source(wpilib, hal_data):
    src = wpilib.DigitalInput(3)
    ctr = wpilib.Counter()
    ctr.setUpSource(src)
    check_init(hal_data, 0, 3, 0, (True, False), (False, False))


def test_counter_set_up_trigger(wpilib, hal_data):
    src = wpilib.AnalogTrigger(4)
    ctr = wpilib.Counter()
    ctr.setUpSource(src, wpilib.AnalogTriggerOutput.AnalogTriggerType.kState)
    # Analog triggers get their channel ids from their index, not their analog port.
    check_init(hal_data, 0, 0, 0, (True, False), (False, False), True)


def test_counter_clear_up_source(wpilib, hal_data):
    ctr = wpilib.Counter(2)
    ctr.clearUpSource()
    check_init(hal_data, 0, 0, 0, (False, False), (False, False))


def test_counter_set_down_channel(wpilib, hal_data):
    ctr = wpilib.Counter()
    ctr.setDownSource(2)
    check_init(hal_data, 0, 0, 2, (False, False), (False, False))
    assert hal_data["dio"][2]["initialized"] == True
    assert hal_data["dio"][2]["is_input"] == True


def test_counter_set_down_source(wpilib, hal_data):
    src = wpilib.DigitalInput(3)
    ctr = wpilib.Counter()
    ctr.setDownSource(src)
    check_init(hal_data, 0, 0, 3, (False, False), (False, False))


def test_counter_set_down_trigger(wpilib, hal_data):
    src = wpilib.AnalogTrigger(4)
    ctr = wpilib.Counter()
    ctr.setDownSource(src, wpilib.AnalogTriggerOutput.AnalogTriggerType.kState)
    # Analog triggers get their channel ids from their index, not their analog port.
    check_init(hal_data, 0, 0, 0, (False, False), (False, False), False, True)


def test_counter_clear_up_source(wpilib, hal_data):
    ctr = wpilib.Counter()
    ctr.setDownSource(2)
    ctr.clearDownSource()
    check_init(hal_data, 0, 0, 0, (False, False), (False, False))


def test_counter_close(hal, wpilib, hal_data):
    assert not hal_data["counter"][0]["initialized"]
    assert not hal_data["dio"][0]["initialized"]
    assert not hal_data["dio"][1]["initialized"]
    ctr = wpilib.Counter()
    ctr.setUpSource(0)
    ctr.setDownSource(1)
    assert hal_data["counter"][0]["initialized"]
    assert hal_data["dio"][0]["initialized"]
    assert hal_data["dio"][1]["initialized"]
    ctr.close()
    with pytest.raises(hal.HALError):
        ctr.get()
    assert not hal_data["counter"][0]["initialized"]
    assert not hal_data["dio"][0]["initialized"]
    assert not hal_data["dio"][1]["initialized"]


@pytest.mark.parametrize(
    "args", [(False, False), (False, True), (True, False), (True, True)]
)
def test_counter_set_up_source_edge(wpilib, hal_data, args):
    ctr = wpilib.Counter()
    ctr.setUpSource(2)
    ctr.setUpSourceEdge(*args)
    assert hal_data["counter"][0]["up_rising_edge"] == args[0]
    assert hal_data["counter"][0]["up_falling_edge"] == args[1]


@pytest.mark.parametrize(
    "args", [(False, False), (False, True), (True, False), (True, True)]
)
def test_counter_set_down_source_edge(wpilib, hal_data, args):
    ctr = wpilib.Counter()
    ctr.setDownSource(2)
    ctr.setDownSourceEdge(*args)
    assert hal_data["counter"][0]["down_rising_edge"] == args[0]
    assert hal_data["counter"][0]["down_falling_edge"] == args[1]


def test_counter_set_updown_mode(wpilib, hal_data):
    ctr = wpilib.Counter()
    ctr.setUpDownCounterMode()
    assert hal_data["counter"][0]["mode"] == 0


def test_counter_set_extdir_mode(wpilib, hal_data):
    ctr = wpilib.Counter()
    ctr.setExternalDirectionMode()
    assert hal_data["counter"][0]["mode"] == 3


@pytest.mark.parametrize("high", [True, False])
def test_counter_set_semi_mode(wpilib, hal_data, high):
    ctr = wpilib.Counter()
    ctr.setSemiPeriodMode(high)
    assert hal_data["counter"][0]["mode"] == 1
    assert hal_data["counter"][0]["up_rising_edge"] == high
    assert not hal_data["counter"][0]["update_when_empty"]


@pytest.mark.parametrize("thresh", [1, 4.5, 1.5])
def test_counter_set_pl_mode(wpilib, hal_data, thresh):
    ctr = wpilib.Counter()
    ctr.setPulseLengthMode(thresh)
    assert hal_data["counter"][0]["mode"] == 2
    assert hal_data["counter"][0]["pulse_length_threshold"] == thresh


def test_counter_get(wpilib, hal_data):
    ctr = wpilib.Counter()
    hal_data["counter"][0]["count"] = 4
    assert ctr.get() == 4
    hal_data["counter"][0]["count"] = 2
    assert ctr.get() == 2


def test_counter_get_distance(wpilib, hal_data):
    ctr = wpilib.Counter()
    ctr.setDistancePerPulse(2)
    hal_data["counter"][0]["count"] = 4
    assert ctr.getDistance() == 4 * 2
    ctr.setDistancePerPulse(5)
    hal_data["counter"][0]["count"] = 2
    assert ctr.getDistance() == 2 * 5


def test_counter_reset(wpilib, hal_data):
    ctr = wpilib.Counter()
    hal_data["counter"][0]["count"] = 4
    assert ctr.get() == 4
    ctr.reset()
    assert hal_data["counter"][0]["count"] == 0
    assert ctr.get() == 0


@pytest.mark.parametrize("period", [1, 4.5, 1.5])
def test_counter_set_max_period(wpilib, hal_data, period):
    ctr = wpilib.Counter()
    assert hal_data["counter"][0]["max_period"] == 0.5
    ctr.setMaxPeriod(period)
    assert hal_data["counter"][0]["max_period"] == period


@pytest.mark.parametrize("enabled", [True, False])
def test_counter_set_update_empty(wpilib, hal_data, enabled):
    ctr = wpilib.Counter()
    assert hal_data["counter"][0]["update_when_empty"] == False
    ctr.setUpdateWhenEmpty(enabled)
    assert hal_data["counter"][0]["update_when_empty"] == enabled


def test_counter_get_stopped(wpilib, hal_data):
    ctr = wpilib.Counter()
    hal_data["counter"][0]["period"] = 6
    hal_data["counter"][0]["max_period"] = 7
    assert not ctr.getStopped()
    hal_data["counter"][0]["period"] = 7
    hal_data["counter"][0]["max_period"] = 3
    assert ctr.getStopped()


@pytest.mark.parametrize("dir", [True, False])
def test_counter_get_direction(wpilib, hal_data, dir):
    ctr = wpilib.Counter()
    hal_data["counter"][0]["direction"] = dir
    assert ctr.getDirection() == dir


@pytest.mark.parametrize("dir", [True, False])
def test_counter_set_reverse_direction(wpilib, hal_data, dir):
    ctr = wpilib.Counter()
    ctr.setReverseDirection(dir)
    assert hal_data["counter"][0]["reverse_direction"] == dir


@pytest.mark.parametrize("period", [1, 5.76, 2.222])
def test_counter_get_period(wpilib, hal_data, period):
    ctr = wpilib.Counter()
    hal_data["counter"][0]["period"] = period
    assert ctr.getPeriod() == period


@pytest.mark.parametrize(
    "period, dist_per_pulse, expected", [(1, 3, 3), (5.76, 1, 0.173), (2.222, 2.222, 1)]
)
def test_counter_get_rate(wpilib, hal_data, period, dist_per_pulse, expected):
    ctr = wpilib.Counter()
    ctr.setDistancePerPulse(dist_per_pulse)
    hal_data["counter"][0]["period"] = period
    assert ctr.getRate() == pytest.approx(expected, 0.01)


@pytest.mark.parametrize("samples", [1, 3, 10])
def test_counter_set_get_samples(wpilib, hal_data, samples):
    ctr = wpilib.Counter()
    ctr.setSamplesToAverage(samples)
    assert hal_data["counter"][0]["samples_to_average"] == samples
    assert ctr.getSamplesToAverage() == samples


def test_counter_set_pid_source_type_invalid(wpilib):
    ctr = wpilib.Counter()
    with pytest.raises(ValueError):
        ctr.setPIDSourceType(-1)


def test_counter_pidget_displacement(wpilib):
    ctr = wpilib.Counter()
    ctr.getDistance = MagicMock()
    ctr.getDistance.return_value = 5.0
    ctr.setPIDSourceType(wpilib.interfaces.PIDSource.PIDSourceType.kDisplacement)
    assert ctr.pidGet() == pytest.approx(5.0, 0.01)


def test_counter_pidget_rate(wpilib):
    ctr = wpilib.Counter()
    ctr.getRate = MagicMock()
    ctr.getRate.return_value = 7.0
    ctr.setPIDSourceType(wpilib.interfaces.PIDSource.PIDSourceType.kRate)
    assert ctr.pidGet() == pytest.approx(7.0, 0.01)


def test_counter_initSendable(wpilib, sendablebuilder, hal_data):
    hal_data["counter"][0]["count"] = 4
    ctr = wpilib.Counter()
    ctr.initSendable(sendablebuilder)

    assert sendablebuilder.properties[0].key == "Value"
    assert sendablebuilder.properties[0].setter is None

    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getNumber("Value", 0.0) == 4
    assert sendablebuilder.getTable().getString(".type", "") == "Counter"


def test_geartooth_init_1(wpilib, hal_data):
    di = wpilib.DigitalInput(5)
    ctr = wpilib.GearTooth(di)
    check_init(
        hal_data, wpilib.Counter.Mode.kTwoPulse, 5, 0, (True, False), (False, False)
    )


def test_geartooth_init_2(wpilib, hal_data):
    di = wpilib.DigitalInput(5)
    ctr = wpilib.GearTooth(di, True)
    check_init(
        hal_data, wpilib.Counter.Mode.kPulseLength, 5, 0, (True, False), (False, False)
    )


def test_geartooth_init_3(wpilib, hal_data):
    ctr = wpilib.GearTooth(6)
    check_init(
        hal_data, wpilib.Counter.Mode.kTwoPulse, 6, 0, (True, False), (False, False)
    )
    assert hal_data["dio"][6]["initialized"] == True
    assert hal_data["dio"][6]["is_input"] == True


def test_geartooth_init_4(wpilib, hal_data):
    ctr = wpilib.GearTooth(6, True)
    check_init(
        hal_data, wpilib.Counter.Mode.kPulseLength, 6, 0, (True, False), (False, False)
    )
    assert hal_data["dio"][6]["initialized"] == True
    assert hal_data["dio"][6]["is_input"] == True


def test_geartooth_initSendable(wpilib, sendablebuilder, hal_data):
    hal_data["counter"][0]["count"] = 4
    ctr = wpilib.GearTooth(6)
    ctr.initSendable(sendablebuilder)

    assert sendablebuilder.properties[0].key == "Value"
    assert sendablebuilder.properties[0].setter is None

    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getNumber("Value", 0.0) == 4
    assert sendablebuilder.getTable().getString(".type", "") == "Gear Tooth"
