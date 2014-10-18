import pytest
from unittest.mock import MagicMock, call

def check_initRelay(channel, direction, relay, hal, wpilib):
    assert relay.channel == channel
    assert relay.direction == direction
    hal.getPort.assert_called_once_with(channel)
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

    check_initRelay(3, direction, relay, hal, wpilib)

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

@pytest.mark.parametrize("dir,value,fwd,rev",
        [("kBoth",      "kOff",     False,  False),
         ("kBoth",      "kOn",      True,   True),
         ("kBoth",      "kForward", True,   False),
         ("kBoth",      "kReverse", False,  True),
         ("kForward",   "kOff",     False,  None),
         ("kForward",   "kOn",      True,   None),
         ("kForward",   "kForward", True,   None),
         ("kForward",   "kReverse", None,   None), # error
         ("kReverse",   "kOff",     None,   False),
         ("kReverse",   "kOn",      None,   True),
         ("kReverse",   "kForward", None,   None), # error
         ("kReverse",   "kReverse", None,   True)])
def test_relay_set(dir, value, fwd, rev, hal, wpilib):
    relay = wpilib.Relay(2, getattr(wpilib.Relay.Direction, dir))
    hal.reset_mock()
    if fwd is None and rev is None:
        with pytest.raises(ValueError):
            relay.set(getattr(wpilib.Relay.Value, value))
    else:
        relay.set(getattr(wpilib.Relay.Value, value))
    if fwd is None:
        assert not hal.setRelayForward.called
    else:
        hal.setRelayForward.assert_called_once_with(relay._port, fwd)
    if rev is None:
        assert not hal.setRelayReverse.called
    else:
        hal.setRelayReverse.assert_called_once_with(relay._port, rev)

def test_relay_set_badvalue(relay, hal):
    with pytest.raises(ValueError):
        relay.set(4)
    assert not hal.setRelayForward.called and not hal.setRelayReverse.called

def test_relay_set_freed(relay, hal):
    relay.free()
    hal.reset_mock()
    with pytest.raises(ValueError):
        relay.set(relay.Value.kOff)
    assert not hal.setRelayForward.called and not hal.setRelayReverse.called

@pytest.mark.parametrize("dir,value,fwd,rev",
        [("kBoth",      "kOff",     False,  False),
         ("kBoth",      "kOn",      True,   True),
         ("kBoth",      "kForward", True,   False),
         ("kBoth",      "kReverse", False,  True),
         ("kForward",   "kOff",     False,  False),
         ("kForward",   "kOn",      True,   False),
         #("kForward",   "kForward", True,   False), # duplicate to kOn
         #("kForward",   "kReverse", None,   None), # error
         ("kReverse",   "kOff",     False,  False),
         ("kReverse",   "kOn",      False,  True),
         #("kReverse",   "kForward", None,   None), # error
         #("kReverse",   "kReverse", False,  True), # duplicate to kOn
         ])
def test_relay_get(dir, value, fwd, rev, hal, wpilib):
    relay = wpilib.Relay(2, getattr(wpilib.Relay.Direction, dir))
    hal.reset_mock()
    hal.getRelayForward.return_value = fwd
    hal.getRelayReverse.return_value = rev
    assert relay.get() == getattr(relay.Value, value)
    hal.getRelayForward.assert_called_once_with(relay._port)
    hal.getRelayReverse.assert_called_once_with(relay._port)

def test_relay_get_freed(relay, hal):
    relay.free()
    hal.reset_mock()
    with pytest.raises(ValueError):
        relay.get()
    assert not hal.setRelayForward.called and not hal.setRelayReverse.called

@pytest.mark.parametrize("origdir,newdir",
        [("kBoth", "kBoth"), ("kBoth", "kForward"), ("kBoth", "kReverse"),
         ("kForward", "kBoth"), ("kForward", "kForward"), ("kForward", "kReverse"),
         ("kReverse", "kBoth"), ("kReverse", "kForward"), ("kReverse", "kReverse")])
def test_relay_setDirection(origdir, newdir, hal, wpilib):
    origdir = getattr(wpilib.Relay.Direction, origdir)
    newdir = getattr(wpilib.Relay.Direction, newdir)
    relay = wpilib.Relay(2, origdir)
    hal.reset_mock()
    relay.setDirection(newdir)
    if origdir != newdir:
        check_initRelay(2, newdir, relay, hal, wpilib)
    else:
        hal.assert_has_calls([])

def test_relay_getSmartDashboardType(relay):
    assert relay.getSmartDashboardType() == "Relay"

@pytest.mark.parametrize("value", [None, "Off", "On", "Forward", "Reverse"])
def test_relay_updateTable(value, relay):
    relay.getTable = MagicMock()
    relay.get = MagicMock()
    if value is None:
        relay.getTable.return_value = None
        relay.updateTable()
        assert not relay.get.called
    else:
        relay.get.return_value = getattr(relay.Value, "k"+value)
        relay.updateTable()
        relay.getTable.return_value.putString.assert_called_once_with("Value", value)

@pytest.mark.parametrize("value", ["inv", "Off", "On", "Forward", "Reverse"])
def test_relay_valueChanged(value, relay):
    relay.set = MagicMock()
    relay.valueChanged(None, None, value, None)
    if value == "inv":
        assert not relay.set.called
    else:
        relay.set.assert_called_once_with(getattr(relay.Value, "k"+value))

