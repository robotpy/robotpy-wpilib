class HALError(RuntimeError):
    pass


class CANError(RuntimeError):
    pass


class CANNotInitializedException(RuntimeError):
    pass


class CANMessageNotFound(CANError):
    pass
