#
# These are opaque types used internally by the simulation HAL
#

from _hal_constants import kMaxJoystickAxes, kMaxJoystickPOVs

# fmt: off
__all__ = [
    "ControlWord", "ControlWord_ptr",
    "JoystickAxes", "JoystickAxes_ptr",
    "JoystickPOVs", "JoystickPOVs_ptr",
    "JoystickButtons", "JoystickButtons_ptr",
    "JoystickDescriptor", "JoystickDescriptor_ptr",
    "CANStreamMessage", "CANStreamMessage_ptr",
    
    "Handle",
    "PortHandle",
    
    "AnalogInputHandle",
    "AnalogOutputHandle",
    "AnalogTriggerHandle",
    "CANHandle",
    "CompressorHandle",
    "CounterHandle",
    "DigitalHandle",
    "DigitalPWMHandle",
    "EncoderHandle",
    "FPGAEncoderHandle",
    "GyroHandle",
    "InterruptHandle",
    "NotifierHandle",
    "PDPHandle",
    "RelayHandle",
    "SolenoidHandle",
]
# fmt: on


class _fakeptr(object):
    fake_pointer = True


# Fake pointer emulating a c.POINTER()
def fake_pointer(orig_obj, name=None):
    if name is None:
        name = orig_obj.__name__
    obj = type(name, (orig_obj,), _fakeptr.__dict__.copy())
    return obj


#############################################################################
# HAL
#
# Profiling note: it seems to be faster to use __slots__ and to not have
#                 constructors for things that are created often, and just
#                 set the attributes externally. Python 3.4, linux
#
#############################################################################


class ControlWord:
    ENABLED_FIELD = 0
    AUTO_FIELD = 1
    TEST_FIELD = 2
    EMERGENCY_STOP_FIELD = 3
    FMS_ATTACHED_FIELD = 4
    DS_ATTACHED_FIELD = 5

    def __init__(self):
        self.enabled = 0
        self.autonomous = 0
        self.test = 0
        self.eStop = 0
        self.fmsAttached = 0
        self.dsAttached = 0

    @property
    def bits(self) -> int:
        return (
            self.enabled << self.ENABLED_FIELD
            | self.autonomous << self.AUTO_FIELD
            | self.test << self.TEST_FIELD
            | self.eStop << self.EMERGENCY_STOP_FIELD
            | self.fmsAttached << self.FMS_ATTACHED_FIELD
            | self.dsAttached << self.DS_ATTACHED_FIELD
        )


ControlWord_ptr = fake_pointer(ControlWord)


class JoystickAxes:
    __slots__ = ["count", "axes"]

    def __init__(self):
        self.count = 0
        self.axes = [0] * kMaxJoystickAxes


JoystickAxes_ptr = fake_pointer(JoystickAxes)


class JoystickPOVs:
    __slots__ = ["count", "povs"]

    def __init__(self):
        self.count = 0
        self.povs = [0] * kMaxJoystickPOVs


JoystickPOVs_ptr = fake_pointer(JoystickPOVs)


class JoystickButtons:
    __slots__ = ["buttons", "count"]

    def __init__(self):
        self.count = 0
        self.buttons = 0


JoystickButtons_ptr = fake_pointer(JoystickButtons)


class JoystickDescriptor:
    __slots__ = ["isXbox", "type", "name", "axisCount", "buttonCount"]

    def __init__(self, d={}):
        self.isXbox = d.get("isXbox", False)
        self.type = d.get("type", 0)
        self.name = d.get("name", "")
        self.axisCount = d.get("axisCount", 0)
        self.buttonCount = d.get("buttonCount", 0)


JoystickDescriptor_ptr = fake_pointer(JoystickDescriptor)


class MatchInfo:
    __slots__ = [
        "eventName",
        "matchType",
        "matchNumber",
        "replayNumber",
        "gameSpecificMessage",
    ]

    def __init__(
        self, *, eventName: bytes = None, gameSpecificMessage: bytes = None
    ) -> None:
        self.eventName = eventName
        self.gameSpecificMessage = gameSpecificMessage


MatchInfo_ptr = fake_pointer(MatchInfo)


class CANStreamMessage:
    __slots__ = ["messageID", "timeStamp", "data", "dataSize"]

    def __init__(self):
        self.messageID = 0
        self.timeStamp = 0
        self.data = bytearray(8)
        self.dataSize = 0


CANStreamMessage_ptr = fake_pointer(CANStreamMessage)

#############################################################################
# Opaque handles
#############################################################################


class Handle:
    __slots__ = ()


class PortHandle(Handle):
    __slots__ = ["pin", "module"]

    def __init__(self, pin, module):
        self.pin = pin
        self.module = module

    def __repr__(self):
        return "<%s at 0x%x pin=%s module=%s>" % (
            self.__class__.__qualname__,
            id(self),
            self.pin,
            self.module,
        )


class AnalogInputHandle(Handle):
    __slots__ = ["pin"]

    def __init__(self, port):
        self.pin = port.pin

    def __repr__(self):
        return "<%s at 0x%x pin=%s>" % (type(self).__qualname__, id(self), self.pin)


class AnalogOutputHandle(Handle):
    __slots__ = ["pin"]

    def __init__(self, port):
        self.pin = port.pin

    def __repr__(self):
        return "<%s at 0x%x pin=%s>" % (type(self).__qualname__, id(self), self.pin)


class AnalogTriggerHandle(Handle):
    __slots__ = ["pin", "index"]

    def __init__(self, port, index):
        self.pin = port.pin
        self.index = index

    def __repr__(self):
        return "<%s at 0x%x pin=%s index=%s>" % (
            type(self).__qualname__,
            id(self),
            self.pin,
            self.index,
        )


class CANHandle(Handle):
    __slots__ = ["manufacturer", "deviceId", "deviceType"]

    def __init__(self, manufacturer: int, deviceId: int, deviceType: int) -> None:
        self.manufacturer = manufacturer
        self.deviceId = deviceId
        self.deviceType = deviceType

    def __repr__(self):
        return "%s(manufacturer=%r, deviceId=%r, deviceType=%r)" % (
            type(self).__qualname__,
            self.manufacturer,
            self.deviceId,
            self.deviceType,
        )


class CompressorHandle(Handle):
    __slots__ = ["module"]

    def __init__(self, module):
        self.module = module

    def __repr__(self):
        return "<%s at 0x%x module=%s>" % (
            type(self).__qualname__,
            id(self),
            self.module,
        )


class CounterHandle(Handle):
    __slots__ = ["idx"]

    def __init__(self, idx):
        self.idx = idx

    def __repr__(self):
        return "<%s at 0x%x idx=%s>" % (type(self).__qualname__, id(self), self.idx)


class DigitalHandle(Handle):
    __slots__ = ["pin"]

    def __init__(self, port):
        self.pin = port.pin

    def __repr__(self):
        return "<%s at 0x%x pin=%s>" % (type(self).__qualname__, id(self), self.pin)


class DigitalPWMHandle(Handle):
    __slots__ = ["pin", "portHandle"]

    def __init__(self, portHandle):
        self.pin = portHandle.pin

    def __repr__(self):
        return "<%s at 0x%x pin=%s>" % (type(self).__qualname__, id(self), self.pin)


class EncoderHandle(Handle):
    __slots__ = ["idx"]

    def __init__(self, idx):
        self.idx = idx

    def __repr__(self):
        return "<%s at 0x%x idx=%s>" % (type(self).__qualname__, id(self), self.idx)


class FPGAEncoderHandle(Handle):
    pass


class GyroHandle(Handle):
    __slots__ = ["pin"]

    def __init__(self, port):
        self.pin = port.pin

    def __repr__(self):
        return "<%s at 0x%x pin=%s>" % (type(self).__qualname__, id(self), self.pin)


class InterruptHandle(Handle):
    pass


class NotifierHandle(Handle):
    def __init__(self):
        self.waitTime = None
        self.updatedAlarm = None
        self.active = True
        self.running = False
        self.lock = None


class PDPHandle(Handle):
    __slots__ = ["module"]

    def __init__(self, module):
        self.module = module

    def __repr__(self):
        return "<%s at 0x%x module=%s>" % (
            type(self).__qualname__,
            id(self),
            self.module,
        )


class RelayHandle(Handle):
    __slots__ = ["pin"]

    def __init__(self, pin):
        self.pin = pin

    def __repr__(self):
        return "<%s at 0x%x pin=%s>" % (type(self).__qualname__, id(self), self.pin)


class SolenoidHandle(Handle):
    __slots__ = ["module", "pin"]

    def __init__(self, port):
        self.module = port.module
        self.pin = port.pin

    def __repr__(self):
        return "<%s at 0x%x mod=%s pin=%s>" % (
            type(self).__qualname__,
            id(self),
            self.module,
            self.pin,
        )
