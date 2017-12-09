import pytest
from unittest.mock import MagicMock, call, patch


@pytest.fixture(scope="function")
def relay(request, wpilib):
    return wpilib.Relay(2)


@pytest.fixture(scope="function")
def relay_data(request, hal_data):
    return hal_data['relay'][2]


@pytest.fixture(scope="function")
def relay_table(networktables):
    return networktables.NetworkTables.getTable("/LiveWindow/Ungrouped/Relay[2]")


def check_initRelay(channel, direction, relay, relay_data, hal, hal_data, wpilib, init=None):
    assert relay.channel == channel
    assert relay.direction == direction
    
    #hal.getPort.assert_called_once_with(channel)
    #hal.initializeDigitalPort.assert_called_once_with(hal.getPort.return_value)
    #assert relay._port == hal.initializeDigitalPort.return_value
    
    if direction == wpilib.Relay.Direction.kBoth:
        assert relay_data['fwd'] == False
        assert relay_data['rev'] == False
        assert relay.channel in hal_data['reports'][hal.HALUsageReporting.kResourceType_Relay]
        assert relay.channel + 128 in hal_data['reports'][hal.HALUsageReporting.kResourceType_Relay] 
        
        #hal.setRelayForward.assert_called_once_with(relay._port, False)
        #hal.setRelayReverse.assert_called_once_with(relay._port, False)
        #hal.HALReport.assert_has_calls(
        #        [call(hal.HALUsageReporting.kResourceType_Relay, relay.channel),
        #         call(hal.HALUsageReporting.kResourceType_Relay, relay.channel + 128)],
        #        any_order=True)
    elif direction == wpilib.Relay.Direction.kForward:
        assert relay_data['fwd'] == False
        assert relay_data['rev'] == init
        assert relay.channel in hal_data['reports'][hal.HALUsageReporting.kResourceType_Relay]
        #hal.setRelayForward.assert_called_once_with(relay._port, False)
        #hal.HALReport.assert_called_once_with(hal.HALUsageReporting.kResourceType_Relay, relay.channel)
    elif direction == wpilib.Relay.Direction.kReverse:
        assert relay_data['fwd'] == init
        assert relay_data['rev'] == False
        assert relay.channel + 128 in hal_data['reports'][hal.HALUsageReporting.kResourceType_Relay]
        #hal.setRelayReverse.assert_called_once_with(relay._port, False)
        #hal.HALReport.assert_called_once_with(hal.HALUsageReporting.kResourceType_Relay, relay.channel + 128)


@pytest.mark.parametrize("direction", [None, "None", "kBoth", "kForward", "kReverse"])
def test_relay_create(direction, hal, hal_data, wpilib, relay_data):
    relay_data['fwd'] = None
    relay_data['rev'] = None
    
    if direction is None:
        relay = wpilib.Relay(2)
        direction = wpilib.Relay.Direction.kBoth
    elif direction == "None":
        relay = wpilib.Relay(2, None)
        direction = wpilib.Relay.Direction.kBoth
    else:
        direction = getattr(wpilib.Relay.Direction, direction)
        relay = wpilib.Relay(2, direction)

    check_initRelay(2, direction, relay, relay_data, hal, hal_data, wpilib)


def test_relay_create_all(wpilib):
    relays = []
    for i in range(wpilib.SensorBase.kRelayChannels):
        relays.append(wpilib.Relay(i))


def test_relay_create_error(hal, wpilib):
    _ = wpilib.Relay(3)
    with pytest.raises(IndexError):
        _ = wpilib.Relay(3)


def test_relay_free(relay, hal, wpilib):
    #wasport = relay._port
    assert relay.forwardHandle == relay._forwardHandle
    assert relay.reverseHandle == relay._reverseHandle

    relay.free()
    
    with pytest.raises(ValueError):
        _ = relay.forwardHandle
    with pytest.raises(ValueError):
        _ = relay.reverseHandle

    #hal.setRelayForward.assert_called_once_with(wasport, False)
    #hal.setRelayReverse.assert_called_once_with(wasport, False)
    #hal.freeDIO.assert_called_once_with(wasport)
    # try to re-grab
    _ = wpilib.Relay(2)
   

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
def test_relay_set(dir, value, fwd, rev, wpilib, relay_data):
    relay = wpilib.Relay(2, getattr(wpilib.Relay.Direction, dir))
    relay_data['fwd'] = None
    relay_data['rev'] = None
    
    if fwd is None and rev is None:    
        with pytest.raises(ValueError):
            relay.set(getattr(wpilib.Relay.Value, value))
    else:
        relay.set(getattr(wpilib.Relay.Value, value))
        
    assert relay_data['fwd'] is fwd
    assert relay_data['rev'] is rev


def test_relay_set_badvalue(relay):
    with pytest.raises(ValueError):
        relay.set(4)
    #assert not hal.setRelayForward.called and not hal.setRelayReverse.called


def test_relay_set_freed(relay):
    relay.free()
    #hal.reset_mock()
    with pytest.raises(ValueError):
        relay.set(relay.Value.kOff)
    #assert not hal.setRelayForward.called and not hal.setRelayReverse.called


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
def test_relay_get(dir, value, fwd, rev, wpilib, relay_data):
    relay = wpilib.Relay(2, getattr(wpilib.Relay.Direction, dir))
    relay_data['fwd'] = fwd
    relay_data['rev'] = rev
    
    #hal.reset_mock()
    #hal.getRelayForward.return_value = fwd
    #hal.getRelayReverse.return_value = rev
    assert relay.get() == getattr(relay.Value, value)
    #hal.getRelayForward.assert_called_once_with(relay._port)
    #hal.getRelayReverse.assert_called_once_with(relay._port)


def test_relay_get_freed(relay, hal):
    relay.free()
    #hal.reset_mock()
    with pytest.raises(ValueError):
        relay.get()
    #assert not hal.setRelayForward.called and not hal.setRelayReverse.called


def test_relay_getChannel(relay):
    assert relay.getChannel() == 2


def test_relay_expiration(relay):
    relay.setExpiration(111)
    assert relay.getExpiration() == 111


def test_relay_isAlive1(relay):
    relay.setSafetyEnabled(False)
    assert relay.isAlive()
    relay.setSafetyEnabled(True)
    assert not relay.isAlive()


def test_relay_isAlive2(wpilib, sim_hooks):
    relay = wpilib.Relay(2)

    relay.setSafetyEnabled(True)
    sim_hooks.time = 1.0
    assert not relay.isAlive()
    relay.feed()
    assert relay.isAlive()
    

def test_relay_stopMotor(relay, wpilib):
    relay.set = MagicMock()
    relay.stopMotor()
    relay.set.assert_called_with(wpilib.Relay.Value.kOff)


@pytest.mark.parametrize('value', [True, False])
def test_relay_isSafetyEnabled(relay, value):
    relay.setSafetyEnabled(value)
    assert relay.isSafetyEnabled() == value


def test_relay_getDescription(relay):
    assert relay.getDescription() == "Relay ID 2"


@pytest.mark.parametrize("origdir,newdir",
        [("kBoth", "kBoth"), ("kBoth", "kForward"), ("kBoth", "kReverse"),
         ("kForward", "kBoth"), ("kForward", "kForward"), ("kForward", "kReverse"),
         ("kReverse", "kBoth"), ("kReverse", "kForward"), ("kReverse", "kReverse")])
def test_relay_setDirection(origdir, newdir, hal, hal_data, wpilib, relay_data):
    relay_data['fwd'] = None
    relay_data['rev'] = None
    origdir = getattr(wpilib.Relay.Direction, origdir)
    newdir = getattr(wpilib.Relay.Direction, newdir)
    relay = wpilib.Relay(2, origdir)
    #hal.reset_mock()
    relay.setDirection(newdir)
    
    init = False if origdir != newdir else None
    check_initRelay(2, newdir, relay, relay_data, hal, hal_data, wpilib, init=init)
    #else:
        #hal.assert_has_calls([])
