import hal
import hal_impl
from hal_impl.sim_hooks import SimHooks as BaseSimHooks


class SimHooks(BaseSimHooks):
    def __init__(self):
        super().__init__()
        self.time = 0.0

    def getTime(self):
        return self.time
