import nivision
import ctypes
import logging
import socket
import struct
import threading
import time

__all__ = ["CameraServer"]

logger = logging.getLogger(__name__)

class CameraServer:
    kPort = 1180
    kMagicNumber = bytes([0x01, 0x00, 0x00, 0x00])
    kSize640x480 = 0
    kSize320x240 = 1
    kSize160x120 = 2
    kHardwareCompression = -1
    kMaxImageSize = 200000

    intStruct = struct.Struct("!i")

    server = None

    @staticmethod
    def _reset():
        CameraServer.server = None

    @staticmethod
    def getInstance():
        if CameraServer.server is None:
            CameraServer.server = CameraServer()
        return CameraServer.server

    def __init__(self):
        self.mutex = threading.RLock()
        self.ready = threading.Event()
        self.dataPool = [(ctypes.c_ubyte * self.kMaxImageSize)(),
                         (ctypes.c_ubyte * self.kMaxImageSize)(),
                         (ctypes.c_ubyte * self.kMaxImageSize)()]
        self.imageData = (None, 0, 0, None)
        self.captureThread = None

        self.quality = 50
        self.hwClient = True
        self.camera = None

        self.serverThread = threading.Thread(target=self._serve, name="CameraServer")
        self.serverThread.daemon = True
        self.serverThread.start()

    def _freeImageData(self, imageData):
        if imageData[3] is not None:
            nivision.imaqDispose(imageData[3])
        elif imageData[0] is not None:
            with self.mutex:
                self.dataPool.append(imageData[0])

    def _setImageData(self, data, size, start=0, vdata=None):
        with self.mutex:
            self._freeImageData(self.imageData)
            self.imageData = (data, size, start, vdata)
        self.ready.set()

    def setImage(self, image):
        """Manually change the image that is served by the MJPEG stream. This
        can be called to pass custom annotated images to the dashboard. Note
        that, for 640x480 video, this method could take between 40 and 50
        milliseconds to complete.

        This shouldn't be called if startAutomaticCapture() is called.

        :param image: The IMAQ image to show on the dashboard
        """
        # Flatten the IMAQ image to a JPEG
        #t0 = time.time()
        vdata, size = nivision.imaqFlatten(image,
                nivision.IMAQ_FLATTEN_IMAGE,
                nivision.IMAQ_COMPRESSION_JPEG, 10 * self.quality)
        data = (ctypes.c_ubyte * size).from_address(vdata)
        #print("flatten: %s" % (time.time() - t0))

        # If "HW" client setting, Find the start of the JPEG data
        #print(size, [x for x in data])
        start = 0
        with self.mutex:
            hwClient = True#self.hwClient
        if hwClient:
            while start < size - 1:
                if data[start] == 0xFF and data[start + 1] == 0xD8:
                    break
                start += 1
            #print(size, start)

        size -= start
        if size <= 2:
            raise ValueError("data size of flattened image is less than 2. Try another camera!")

        self._setImageData(data, size, start, vdata)

    def startAutomaticCapture(self, camera):
        """Start automatically capturing images to send to the dashboard.

        You should call this method to just see a camera feed on the dashboard
        without doing any vision processing on the roboRIO. {@link #setImage}
        shouldn't be called after this is called.

        :param camera: The camera interface (e.g. a USBCamera instance)
        """
        if self.captureThread is not None:
            return

        self.camera = camera
        self.camera.startCapture()

        self.captureThread = threading.Thread(target=self._autoCapture, name="CaptureThread")
        self.captureThread.daemon = True
        self.captureThread.start()

    def _autoCapture(self):
        frame = nivision.imaqCreateImage(nivision.IMAQ_IMAGE_RGB, 0)

        while True:
            with self.mutex:
                hwClient = True#self.hwClient
                if hwClient:
                    data = self.dataPool[-1]
                    self.dataPool.pop()
            try:
                if hwClient:
                    size = self.camera.getImageData(data, self.kMaxImageSize)
                    self._setImageData(data, size)
                else:
                    self.camera.getImage(frame)
                    self.setImage(frame)
            except (ValueError, IndexError):
                logger.exception("getting image")
                if hwClient and not self.ready.is_set():
                    self.dataPool.append(data)
                time.sleep(0.1)

    def isAutoCaptureStarted(self):
        """check if auto capture is started
        """
        with self.mutex:
            return self.captureThread is not None

    def setSize(self, size):
        if size == self.kSize160x120:
            self.camera.setSize(160, 120)
        elif size == self.kSize320x240:
            self.camera.setSize(320, 240)
        elif size == self.kSize640x480:
            self.camera.setSize(640, 480)
        else:
            return

    def setQuality(self, quality):
        """Set the quality of the compressed image sent to the dashboard

        :param quality: The quality of the JPEG image, from 0 to 100
        """
        with self.mutex:
            if quality > 100:
                self.quality = 100
            elif quality < 0:
                self.quality = 0
            else:
                self.quality = quality

    def getQuality(self):
        """Get the quality of the compressed image sent to the dashboard

        :returns: The quality, from 0 to 100
        """
        with self.mutex:
            return self.quality

    def _serve(self):
        """Run the M-JPEG server.

        This function listens for a connection from the dashboard in a
        background thread, then sends back the M-JPEG stream.
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.kPort))
        sock.listen(1)

        while True:
            try:
                conn, addr = sock.accept()

                s = conn.makefile('rwb')

                fps = self.intStruct.unpack(s.read(4))[0]
                compression = self.intStruct.unpack(s.read(4))[0]
                size = self.intStruct.unpack(s.read(4))[0]
                logger.info("Client connected: %d fps, %d compression, %d size"
                            % (fps, compression, size))

                with self.mutex:
                    doWait = self.camera is None

                if doWait:
                    logger.info("camera not ready yet, awaiting first image")
                    self.ready.wait()

                if compression == self.kHardwareCompression:
                    hwClient = True
                else:
                    hwClient = False
                    self.setQuality(100-compression)

                with self.mutex:
                    self.hwClient = hwClient
                    self.camera.setFPS(fps)
                self.setSize(size)

                period = 1.0 / fps
                while True:
                    t0 = time.time()

                    self.ready.wait()
                    self.ready.clear()

                    imageData = (None, 0, 0, None)
                    try:
                        with self.mutex:
                            imageData = self.imageData
                            self.imageData = (None, 0, 0, None)

                        if imageData[0] is None:
                            continue

                        size = imageData[1]
                        start = imageData[2]
                        data = (ctypes.c_ubyte * size).from_address(ctypes.addressof(imageData[0])+start)

                        #print("sending image")
                        s.write(self.kMagicNumber)
                        # write size of image
                        s.write(self.intStruct.pack(size))
                        s.write(data)
                    except IOError:
                        # print error to driverstation
                        logger.exception("error sending image")
                        break
                    finally:
                        self._freeImageData(imageData)

                    s.flush()
                    dt = time.time() - t0
                    #print(dt, period)
                    if dt < period:
                        time.sleep(period - dt)
            except IOError:
                # print error to driverstation
                logger.exception("error in conn")
                continue

