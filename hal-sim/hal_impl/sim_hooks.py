import threading
import time

from .data import hal_data


class SimHooks:
    """
        These are useful hooks to override for simulations.
    
        To use your own hook, set hal_impl.functions.hooks
    """

    def __init__(self):
        self.initialized = False
        self.reset()

    #
    # Time related hooks
    #

    def getTime(self):
        return time.monotonic()

    def getFPGATime(self):
        return int((self.getTime() - hal_data["time"]["program_start"]) * 1000000)

    def delayMillis(self, ms):
        time.sleep(0.001 * ms)

    def delaySeconds(self, s):
        time.sleep(s)

    def createCondition(self, lock=None):
        return threading.Condition(lock=lock)

    #
    # DriverStation related hooks
    #

    def initializeDriverStation(self):
        if not self.initialized:
            self.ds_cond = threading.Condition()

            self.initialized = True
            self.ds_packets = 0
            self.local = threading.local()

    def isNewControlData(self):
        with self.ds_cond:
            current_count = self.ds_packets

        if getattr(self.local, "count", -1) == current_count:
            return False
        self.local.count = current_count
        return True

    def notifyDSData(self):
        with self.ds_cond:
            self.ds_packets += 1
            self.ds_cond.notify_all()

    def waitForDSData(self, timeout=None):
        with self.ds_cond:
            current_count = self.ds_packets
            return self.ds_cond.wait_for(
                lambda: current_count != self.ds_packets, timeout=timeout
            )

    #
    # Resets this class so it can be reused
    #

    def reset(self):
        if self.initialized:
            self.notifyDSData()

        self.initialized = False
        self.ds_cond = None
        self.ds_packets = None
        self.local = None
