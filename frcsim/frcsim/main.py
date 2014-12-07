
from .controller import Controller

from .types.driverstation import DriverStationControl
from .types.analog_input import SimAnalogInput
from .types.digital_input import SimDigitalInput
from .types.pwm import SimPWM
from .types.timer import Timer

from .hal_hooks import GazeboSimHooks

from hal_impl import data, functions

class FrcSimMain:
    '''
        Connects robot code to gazebo simulator
    '''
    
    def __init__(self, parser):
        parser.add_argument('--host', default='127.0.0.1',
                            help='Hostname of gazebo')
        parser.add_argument('--port', default=11345,
                            help='Port to connect to')
        
        # cache of various devices
        self.devices = {}
    
    def _create_cb(self, typename, i, d, thing_cls):
        # typename: name of object
        # i: channel of object
        # d: dictionary
        # thing_cls: class to create when initialized
        
        self.devices.setdefault(typename, {})
        
        def _cb(k, v):
            # don't initialize the device twice
            # -> TODO: destroy device when freed
            if v and i not in self.devices[typename]:
                self.devices[typename][i] = thing_cls(i, d)
        
        return _cb
    
    def run(self, options, robot_class):

        # TODO: filter out debug logs for pygazebo, as it's pretty noisy

        # Connect to the simulator
        self.controller = Controller(options.host,
                                     options.port)
        
        self.controller.start()
        
        try:
        
            # setup the HAL hooks
            
            # setup various control objects
            self.ds = DriverStationControl(self.controller)
            self.tm = Timer(self.controller)
            
            # HAL Hooks
            self.hal_hooks = GazeboSimHooks(self.tm)
            functions.hooks = self.hal_hooks
            data.reset_hal_data(functions.hooks)
            
            # Analog
            for i, d in enumerate(data.hal_data['analog_in']):
                d.register('initialized', self._create_cb('analog', i, d, SimAnalogInput))
            
            # Digital
            for i, d in enumerate(data.hal_data['dio']):
                d.register('initialized', self._create_cb('dio', i, d, SimDigitalInput))
            
            # Encoders
            
            # PWM
            for i, d in enumerate(data.hal_data['pwm']):
                d.register('initialized', self._create_cb('pwm', i, d, SimPWM))
            
            return robot_class.main(robot_class)
            
        finally:
            self.controller.stop()
