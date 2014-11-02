


class HALError(RuntimeError):
    pass

class CANError(RuntimeError):
    pass

class CANMessageNotFound(CANError):
    pass

