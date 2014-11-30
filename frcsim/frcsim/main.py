
from .controller import Controller

from .types.driverstation import DriverStationControl

class FrcSimMain:
    '''
        Connects robot code to gazebo simulator
    '''
    
    def __init__(self, parser):
        parser.add_argument('--host', default='127.0.0.1',
                            help='Hostname of gazebo')
        parser.add_argument('--port', default=11345,
                            help='Port to connect to')
    
    def run(self, options, robot_class):

        # TODO: filter out debug logs for pygazebo, as it's pretty noisy

        # Connect to the simulator
        self.controller = Controller(options.host,
                                     options.port)
        
        self.controller.start()
        
        try:
        
            # setup the HAL hooks
            
            # setup the driverstation control object
            self.ds = DriverStationControl(self.controller)
            
            robot_class.main(robot_class)
            
        finally:
            self.controller.stop()
