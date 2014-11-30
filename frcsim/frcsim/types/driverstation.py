
import functools

from ..msgs.driver_station_pb2 import DriverStation
from ..msgs.joystick_pb2 import Joystick

import hal
from hal_impl import data

class DriverStationControl:

    def __init__(self, controller):

        controller.subscribe('ds/state',
                             'gazebo.msgs.DriverStation',
                             self.on_state)

        for i in range(6):
            controller.subscribe('ds/joysticks/%s' % i,
                                 'gazebo.msgs.Joystick',
                                 functools.partial(self.on_joystick, i))

        self.state = None
        self.enabled = None

    def on_joystick(self, idx, msg):
        
        js = data.hal_data['joysticks'][idx]
        buttons = js['buttons']
        axes = js['axes']
        
        msg = Joystick.FromString(msg)
        
        # super inefficient, but could be worse..
        # -> probably will be bit by race conditions here 
        for i, (a, _) in enumerate(zip(msg.axes, axes)):
            axes[i] = a
            
        for i, (b, _) in enumerate(zip(msg.buttons, buttons)):
            buttons[i] = b

    def on_state(self, msg):
        state = DriverStation.FromString(msg)
        
        if self.state != state.state or self.enabled != state.enabled:
            
            autonomous = False
            test = False
            
            if state.state == DriverStation.TEST:
                test = True
            elif state.state == DriverStation.AUTO:
                autonomous = True
            elif state.state == DriverStation.TELEOP:
                pass
            
            data.hal_data['control'].update({
                'autonomous': autonomous,
                'test': test,
                'enabled': state.enabled,
                'ds_attached': True
            })
             
            # this notifies the driver station that new data is available
            hal.giveMultiWait(data.hal_newdata_sem)
            
            self.state = state.state
            self.enabled = state.enabled
    