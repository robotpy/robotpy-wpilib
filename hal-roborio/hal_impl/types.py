# fmt: off

import ctypes as C

from _hal_constants import kMaxJoystickAxes, kMaxJoystickPOVs

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

#############################################################################
# HAL
#############################################################################

class _ControlWord(C.Structure):
    _fields_ = [("enabled", C.c_uint32, 1),
                ("autonomous", C.c_uint32, 1),
                ("test", C.c_uint32, 1),
                ("eStop", C.c_uint32, 1),
                ("fmsAttached", C.c_uint32, 1),
                ("dsAttached", C.c_uint32, 1),
                ("control_reserved", C.c_uint32, 26)]

class ControlWord(C.Union):
    _anonymous_ = ("_",)
    _fields_ = [("_", _ControlWord), ("bits", C.c_uint32)]

ControlWord_ptr = C.POINTER(ControlWord)

class JoystickAxes(C.Structure):
    _fields_ = [("count", C.c_uint16),
                ("axes", C.c_float * kMaxJoystickAxes)]
JoystickAxes_ptr = C.POINTER(JoystickAxes)

class JoystickPOVs(C.Structure):
    _fields_ = [("count", C.c_uint16),
                ("povs", C.c_int16 * kMaxJoystickPOVs)]
JoystickPOVs_ptr = C.POINTER(JoystickPOVs)

class JoystickButtons(C.Structure):
    _fields_ = [("buttons", C.c_uint32),
                ("count", C.c_uint8)]
JoystickButtons_ptr = C.POINTER(JoystickButtons)

class JoystickDescriptor(C.Structure):
    _fields_ = [("isXbox", C.c_uint8),
                ("type", C.c_uint8),
                ("name", C.c_char * 256),
                ("axisCount", C.c_uint8),
                ("axisTypes", C.c_uint8 * kMaxJoystickAxes),
                ("buttonCount", C.c_uint8),
                ("povCount", C.c_uint8)]
JoystickDescriptor_ptr = C.POINTER(JoystickDescriptor)

class MatchInfo(C.Structure):
    _fields_ = [("eventName", C.c_char * 64),
                ("matchType", C.c_int),
                ("matchNumber", C.c_uint16),
                ("replayNumber", C.c_uint8),
                ("gameSpecificMessage", C.c_char * 64),
                ("gameSpecificMessageSize", C.c_uint16)]
MatchInfo_ptr = C.POINTER(MatchInfo)


class CANStreamMessage(C.Structure):
    _fields_ = [
        ("messageID", C.c_uint32),
        ("timeStamp", C.c_uint32),
        ("data", C.c_uint8 * 8),
        ("dataSize", C.c_uint8),
    ]

CANStreamMessage_ptr = C.POINTER(CANStreamMessage)

#############################################################################
# Handles
#############################################################################

kInvalidHandle = 0
Handle = C.c_int32

PortHandle = Handle

AnalogInputHandle = Handle
AnalogOutputHandle = Handle
AnalogTriggerHandle = Handle
CANHandle = Handle
CompressorHandle = Handle
CounterHandle = Handle
DigitalHandle = Handle
DigitalPWMHandle = Handle
EncoderHandle = Handle
FPGAEncoderHandle = Handle
GyroHandle = Handle
InterruptHandle = Handle
NotifierHandle = Handle
PDPHandle = Handle
RelayHandle = Handle
SolenoidHandle = Handle
