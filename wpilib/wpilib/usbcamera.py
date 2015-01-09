import nivision
import logging
import re
import threading
import time

__all__ = ["USBCamera"]

logger = logging.getLogger(__name__)

def getJpegSize(data):
    if data[0] != 0xff or data[1] != 0xd8:
        raise ValueError("invalid image")
    pos = 2
    while True:
        if data[pos] != 0xff:
            raise ValueError("invalid image at pos %d (%x)" % (pos, data[pos]))
        t = data[pos+1]
        if t == 0x01 or t >= 0xd0 and t <= 0xd7: # various
            pos += 2
        elif t == 0xd9: # EOI
            return pos + 2
        elif t == 0xd8: # SOI
            raise ValueError("invalid image")
        elif t == 0xda: # SOS
            len = ((data[pos+2] & 0xff) << 8) | (data[pos+3] & 0xff)
            pos += len + 2
            # Find next marker.  Skip over escaped and RST markers.
            while data[pos] != 0xff or data[pos+1] == 0x00 or (data[pos+1] >= 0xd0 and data[pos+1] <= 0xd7):
                pos += 1
        else: # various
            len = ((data[pos+2] & 0xff) << 8) | (data[pos+3] & 0xff)
            pos += len + 2

class USBCamera:
    kDefaultCameraName = b"cam0"

    ATTR_WB_MODE = b"CameraAttributes::WhiteBalance::Mode"
    ATTR_WB_VALUE = b"CameraAttributes::WhiteBalance::Value"
    ATTR_EX_MODE = b"CameraAttributes::Exposure::Mode"
    ATTR_EX_VALUE = b"CameraAttributes::Exposure::Value"
    ATTR_BR_MODE = b"CameraAttributes::Brightness::Mode"
    ATTR_BR_VALUE = b"CameraAttributes::Brightness::Value"

    class WhiteBalance:
        kFixedIndoor = 3000
        kFixedOutdoor1 = 4000
        kFixedOutdoor2 = 5000
        kFixedFluorescent1 = 5100
        kFixedFlourescent2 = 5200

    reMode = re.compile(b"(?P<width>[0-9]+)\s*x\s*(?P<height>[0-9]+)\s+(?P<format>.*?)\s+(?P<fps>[0-9.]+)\s*fps")

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
        with self.mutex:
            for i in range(3):
                try:
                    self.id = nivision.IMAQdxOpenCamera(self.name,
                            nivision.IMAQdxCameraControlModeController)
                except nivision.ImaqDxError as e:
                    if i == 2:
                        raise
                    time.sleep(2.0)
                    continue
                break

    def closeCamera(self):
        with self.mutex:
            if self.id is None:
                return
            nivision.IMAQdxCloseCamera(self.id)
            self.id = None

    def startCapture(self):
        with self.mutex:
            if self.id is None or self.active:
                return
            nivision.IMAQdxConfigureGrab(self.id)
            nivision.IMAQdxStartAcquisition(self.id)
            self.active = True

    def stopCapture(self):
        with self.mutex:
            if self.id is None or not self.active:
                return
            nivision.IMAQdxStopAcquisition(self.id)
            nivision.IMAQdxUnconfigureAcquisition(self.id)
            self.active = False

    def updateSettings(self):
        with self.mutex:
            wasActive = self.active
            # Stop acquistion, close and reopen camera
            if wasActive:
                self.stopCapture()
            if self.id is not None:
                self.closeCamera()
            self.openCamera()

            # Video Mode
            modes, currentMode = nivision.IMAQdxEnumerateVideoModes(self.id)
            foundMode = None
            foundFps = 1000
            for mode in modes:
                m = self.reMode.match(mode.Name)
                if not m:
                    continue
                if int(m.group("width")) != self.width:
                    continue
                if int(m.group("height")) != self.height:
                    continue
                fps = float(m.group("fps"))
                if fps < self.fps:
                    continue
                if fps > foundFps:
                    continue
                isJpeg = m.group("format") in (b"jpeg", b"JPEG")
                if (self.useJpeg and not isJpeg) or (not self.useJpeg and isJpeg):
                    continue
                foundMode = mode
                foundFps = fps
            if foundMode is not None:
                logger.info("found mode %d: %s" % (foundMode.Value, foundMode.Name))
                if foundMode.Value != currentMode.value:
                    nivision.IMAQdxSetAttribute(self.id, nivision.IMAQdxAttributeVideoMode, foundMode)

            # White Balance
            if self.whiteBalance == "auto":
                nivision.IMAQdxSetAttribute(self.id, self.ATTR_WB_MODE, b"Auto")
            else:
                nivision.IMAQdxSetAttribute(self.id, self.ATTR_WB_MODE, b"Manual")
                if self.whiteBalanceValue is not None:
                    nivision.IMAQdxSetAttribute(self.id, self.ATTR_WB_VALUE, self.whiteBalanceValue)

            # Exposure
            if self.exposure == "auto":
                nivision.IMAQdxSetAttribute(self.id, self.ATTR_EX_MODE, b"AutoAperaturePriority")
            else:
                nivision.IMAQdxSetAttribute(self.id, self.ATTR_EX_MODE, b"Manual")
                if self.exposureValue is not None:
                    minv = nivision.IMAQdxGetAttributeMinimum(self.id, self.ATTR_EX_VALUE)
                    maxv = nivision.IMAQdxGetAttributeMaximum(self.id, self.ATTR_EX_VALUE)
                    val = minv + ((maxv - minv) * (self.exposureValue / 100.0))
                    nivision.IMAQdxSetAttribute(self.id, self.ATTR_EX_VALUE, val)

            # Brightness
            nivision.IMAQdxSetAttribute(self.id, self.ATTR_BR_MODE, b"Manual")
            minv = nivision.IMAQdxGetAttributeMinimum(self.id, self.ATTR_BR_VALUE)
            maxv = nivision.IMAQdxGetAttributeMaximum(self.id, self.ATTR_BR_VALUE)
            val = minv + ((maxv - minv) * (self.brightness / 100.0))
            nivision.IMAQdxSetAttribute(self.id, self.ATTR_BR_VALUE, val)

            # Restart acquisition
            if wasActive:
                self.startCapture()

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

            #t0 = time.time()
            nivision.IMAQdxGrab(self.id, image, 1)
            #print("grab: %s" % (time.time() - t0))

    def getImageData(self, data, maxsize):
        with self.mutex:
            if self.needSettingsUpdate or not self.useJpeg:
                self.needSettingsUpdate = False
                self.useJpeg = True
                self.updateSettings()

            #t0 = time.time()
            nivision.IMAQdxGetImageData(self.id, data, maxsize,
                    nivision.IMAQdxBufferNumberModeLast, 0)
            #print("get image data: %s" % (time.time() - t0))
            return getJpegSize(data)

