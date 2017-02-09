# notrack

import hal
import threading

import logging
logger = logging.getLogger('wpilib.cs')

__all__ = ['CameraServer']

class CameraServer:
    '''
        Provides a way to launch an out of process cscore-based camera
        service instance, for streaming or for image processing.
        
        .. note:: This does not correspond directly to the wpilib
                  CameraServer object; that can be found as
                  :class:`cscore.CameraServer`. However, you should
                  not use cscore directly from your robot code, see
                  the documentation for details             
    '''
    
    _alive = False
    _launched = False
    
    @classmethod
    def is_alive(cls):
        ''':returns: True if the CameraServer is still alive'''
        return cls._alive
    
    @classmethod
    def launch(cls, vision_py=None):
        '''
            Launches the CameraServer process in autocapture mode or
            using a user-specified python script
        
            :param vision_py: If specified, this is the relative path to
                              a filename with a function in it
                              
            Example usage::
            
                wpilib.CameraServer.launch("vision.py:main")
            
            .. warning:: You must have robotpy-cscore installed, or this
                         function will fail without returning an error
                         (you will see an error in the console).
                         
        '''
        
        if cls._launched:
            return
        
        cls._launched = True
        
        if hal.isSimulation():
            logger.info("Would launch CameraServer with vision_py=%s", vision_py)
            cls._alive = True
        else:
            logger.info("Launching CameraServer process")
            
            # Launch the cscore launcher in a separate process
            
            import subprocess
            import sys
            
            args = [
                sys.executable,
                '-m', 'cscore'
            ]
            
            if vision_py:
                if not vision_py.startswith('/'):
                    vision_py = '/home/lvuser/py/' + vision_py
                args.append(vision_py)
            
            # We open a pipe to it so that when this process exits, it dies
            proc = subprocess.Popen(args, close_fds=True, stdin=subprocess.PIPE, cwd='/home/lvuser/py')
            th = threading.Thread(target=cls._monitor_child, args=(proc,))
            th.daemon = True
            th.start()
           
    @classmethod 
    def _monitor_child(cls, proc):
        proc.wait()
        logger.warning("CameraServer process exited with exitcode %s", proc.returncode)
        cls._alive = False
                