import pytest
from unittest.mock import call

@pytest.mark.parametrize("direction", [None, "None", "kBoth", "kForward", "kReverse"])
def test_relay_create(direction, hal, wpilib):
    if direction is None:
        relay = wpilib.Relay(3)
        direction = wpilib.Relay.Direction.kBoth
    elif direction == "None":
        relay = wpilib.Relay(3, None)
        direction = wpilib.Relay.Direction.kBoth
    else:
        direction = getattr(wpilib.Relay.Direction, direction)
        relay = wpilib.Relay(3, direction)

    assert relay.channel == 3
    assert relay.direction == direction
    hal.getPort.assert_called_once_with(3)
    hal.initializeDigitalPort.assert_called_once_with(hal.getPort.return_value)
    assert relay._port == hal.initializeDigitalPort.return_value

    if direction == wpilib.Relay.Direction.kBoth:
        hal.setRelayForward.assert_called_once_with(relay._port, False)
        hal.setRelayReverse.assert_called_once_with(relay._port, False)
        hal.HALReport.assert_has_calls(
                [call(hal.HALUsageReporting.kResourceType_Relay, relay.channel),
                 call(hal.HALUsageReporting.kResourceType_Relay, relay.channel + 128)],
                any_order=True)
    elif direction == wpilib.Relay.Direction.kForward:
        hal.setRelayForward.assert_called_once_with(relay._port, False)
        hal.HALReport.assert_called_once_with(hal.HALUsageReporting.kResourceType_Relay, relay.channel)
    elif direction == wpilib.Relay.Direction.kReverse:
        hal.setRelayReverse.assert_called_once_with(relay._port, False)
        hal.HALReport.assert_called_once_with(hal.HALUsageReporting.kResourceType_Relay, relay.channel + 128)

def test_relay_create_error(hal, wpilib):
    relay1 = wpilib.Relay(3)
    with pytest.raises(IndexError):
        relay2 = wpilib.Relay(3)

@pytest.fixture(scope="function")
def relay(wpilib, hal):
    relay = wpilib.Relay(2)
    hal.reset_mock()
    return relay

def test_relay_free(relay, hal, wpilib):
    wasport = relay._port
    assert relay.port == relay._port
    relay.free()
    assert relay.port is None
    hal.setRelayForward.assert_called_once_with(wasport, False)
    hal.setRelayReverse.assert_called_once_with(wasport, False)
    hal.freeDIO.assert_called_once_with(wasport)
    # try to re-grab
    relay2 = wpilib.Relay(2)

