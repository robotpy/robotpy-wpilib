import threading

__all__ = ["USBCamera", "CameraServer"]

class USBCamera:
    kDefaultCameraName = b"cam0"

    class WhiteBalance:
        kFixedIndoor = 3000
        kFixedOutdoor1 = 4000
        kFixedOutdoor2 = 5000
        kFixedFluorescent1 = 5100
        kFixedFlourescent2 = 5200

    def __init__(self, name=None):
        if name is None:
            name = USBCamera.kDefaultCameraName
        self.name = name
        self.id = None
        self.active = False
        self.useJpeg = True

        self.mutex = threading.RLock()

        self.width = 320
        self.height = 240
        self.fps = 30
        self.whiteBalance = "auto"
        self.whiteBalanceValue = None
        self.exposure = "auto"
        self.exposureValue = None
        self.brightness = 50
        self.needSettingsUpdate = True

        self.openCamera()

    def openCamera(self):
        pass

    def closeCamera(self):
        pass

    def startCapture(self):
        self.active = True

    def stopCapture(self):
        self.active = False

    def updateSettings(self):
        pass

    def setFPS(self, fps):
        with self.mutex:
            if fps != self.fps:
                self.needSettingsUpdate = True
                self.fps = fps

    def setSize(self, width, height):
        with self.mutex:
            if width != self.width or height != self.height:
                self.needSettingsUpdate = True
                self.width = width
                self.height = height

    def setBrightness(self, brightness):
        """Set the brightness, as a percentage (0-100).
        """
        with self.mutex:
            if brightness > 100:
                self.brightness = 100
            elif brightness < 0:
                self.brightness = 0
            else:
                self.brightness = brightness
            self.needSettingsUpdate = True

    def getBrightness(self):
        """Get the brightness, as a percentage (0-100).
        """
        with self.mutex:
            return self.brightness

    def setWhiteBalanceAuto(self):
        """Set the white balance to auto.
        """
        with self.mutex:
            self.whiteBalance = "auto"
            self.whiteBalanceValue = None
            self.needSettingsUpdate = True

    def setWhiteBalanceHoldCurrent(self):
        """Set the white balance to hold current.
        """
        with self.mutex:
            self.whiteBalance = "manual"
            self.whiteBalanceValue = None
            self.needSettingsUpdate = True

    def setWhiteBalanceManual(self, value):
        """Set the white balance to manual, with specified color temperature.
        """
        with self.mutex:
            self.whiteBalance = "manual"
            self.whiteBalanceValue = value
            self.needSettingsUpdate = True

    def setExposureAuto(self):
        """Set the exposure to auto aperature.
        """
        with self.mutex:
            self.exposure = "auto"
            self.exposureValue = None
            self.needSettingsUpdate = True

    def setExposureHoldCurrent(self):
        """Set the exposure to hold current.
        """
        with self.mutex:
            self.exposure = "manual"
            self.exposureValue = None
            self.needSettingsUpdate = True

    def setExposureManual(self, value):
        """Set the exposure to manual, as a percentage (0-100).
        """
        with self.mutex:
            self.exposure = "manual"
            if value > 100:
                self.exposureValue = 100
            elif value < 0:
                self.exposureValue = 0
            else:
                self.exposureValue = value
            self.needSettingsUpdate = True

    def getImage(self, image):
        with self.mutex:
            if self.needSettingsUpdate or self.useJpeg:
                self.needSettingsUpdate = False
                self.useJpeg = False
                self.updateSettings()
        raise NotImplementedError

    def getImageData(self, data, maxsize):
        with self.mutex:
            if self.needSettingsUpdate or not self.useJpeg:
                self.needSettingsUpdate = False
                self.useJpeg = True
                self.updateSettings()
        return 0

class CameraServer:
    kPort = 1180
    kSize640x480 = 0
    kSize320x240 = 1
    kSize160x120 = 2

    server = None

    @staticmethod
    def getInstance():
        if CameraServer.server is None:
            CameraServer.server = CameraServer()
        return CameraServer.server

    def __init__(self):
        self.mutex = threading.RLock()
        self.ready = threading.Event()
        self.quality = 50
        self.camera = None

    def setImage(self, image):
        pass

    def startAutomaticCapture(self, camera):
        """Start automatically capturing images to send to the dashboard.

        You should call this method to just see a camera feed on the dashboard
        without doing any vision processing on the roboRIO. {@link #setImage}
        shouldn't be called after this is called.

        :param camera: The camera interface (e.g. a USBCamera instance)
        """
        if self.camera is not None:
            return

        self.camera = camera
        self.camera.startCapture()

    def isAutoCaptureStarted(self):
        """check if auto capture is started
        """
        with self.mutex:
            return self.camera is not None

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

