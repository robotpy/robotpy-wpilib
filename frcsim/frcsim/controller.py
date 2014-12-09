
import asyncio
import threading

import pygazebo

import concurrent.futures

import logging
logger = logging.getLogger('frcsim')


class PublishWrapper:
    def __init__(self, publisher, loop):
        self.publisher = publisher
        self.loop = loop
        
    def publish(self, msg):
        self.loop.call_soon_threadsafe(lambda: self.publisher.publish(msg))

class Controller:
    '''
        Provides access to gazebo
    '''
    
    @staticmethod
    def get():
        return Controller.instance
    
    def __init__(self, host, port):
        
        if hasattr(Controller, 'instance'):
            raise ValueError("Controller instance already created!")
        
        self._host = host
        self._port = port
        
        self.start_event = concurrent.futures.Future()
        
        self._io_thread = threading.Thread(target=self._io_thread_fn, name='io-thread')
        self._io_thread.daemon = True
        
        Controller.instance = self
    
    def _io_thread_fn(self):
        try:
            asyncio.set_event_loop(asyncio.SelectorEventLoop())
            self.loop = asyncio.get_event_loop()
            
            self.loop.run_until_complete(self._io_task_fn())
        except:
            logger.exception("Error in simulation communication thread")

    @asyncio.coroutine
    def _io_task_fn(self):
        '''Runs until the simulation is done'''
        
        self.stop_event = asyncio.Future()
        
        try:
            logger.info("Connecting to gazebo...")
            
            retries = 5
            
            while True:
                try:
                    self.manager = yield from pygazebo.connect(address=(self._host, self._port))
                except ConnectionRefusedError:
                    if retries == 0:
                        raise
                    
                    logger.info("Error connecting to %s:%s, trying again (%s retries left)...", self._host, self._port, retries)
                    retries -= 1    
                    yield from asyncio.sleep(1)
                else:
                    break
            
        except Exception as e:
            self.start_event.set_exception(e)
        else:
            logger.info("Connected!")
            
            self.start_event.set_result(None)
            
            # Wait until done
            yield from self.stop_event
            
        logger.info("Gazebo communication thread is exiting")
    
    #
    # Public API
    #
    
    def start(self):
        '''
            Call this to connect to gazebo, it won't return until the
            connection has been established.
        '''
        
        self._io_thread.start()
        
        # Waits for connection to occur
        self.start_event.result()
        
    
    def stop(self):
        
        def _stop():
            self.stop_event.set_result(None)
        
        self.loop.call_soon_threadsafe(_stop)
        self._io_thread.join(5)

    def advertise(self, topic, msg_type):
        '''
            Gets a publisher -- waits infinitely
            
            Not called from the event loop thread
        '''
        
        # Intentionally not an asyncio future, as this is called from other threads
        fut = concurrent.futures.Future()
        
        @asyncio.coroutine
        def _advertise():
            try:
                publisher = yield from self.manager.advertise('/gazebo/frc/%s' % topic,
                                                              msg_type)
                fut.set_result(publisher)
            except Exception as e:
                fut.set_exception(e)
        
        self.loop.call_soon_threadsafe(lambda: asyncio.async(_advertise()))
        
        # this blocks        
        publisher = fut.result()
        return PublishWrapper(publisher, self.loop)

    def subscribe(self, topic, msg_type, callback):
        '''
            Subscribes to a gazebo message type
        
            Not called from the event loop thread
        '''
        
        def _subscribe():
            try:
                self.manager.subscribe('/gazebo/frc/%s' % topic,
                                       msg_type,
                                       callback)
            except:
                logger.exception("Error subscribing to %s", topic)
        
        self.loop.call_soon_threadsafe(_subscribe)
    