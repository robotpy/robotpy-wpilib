#  Copyright  = c FIRST 2008-2012. All Rights Reserved.
#  Open Source Software - may be modified and shared by FRC teams. The code
#  must be accompanied by the FIRST BSD license file in the root directory of
#  the project.
import enum


class BuiltInWidgetTypes(enum.Enum):
    kTextView = "Text View"
    kNumberSlider = "Number Slider"

    kNumberBar = "Number Bar"

    kDial = "Simple Dial"

    kGraph = "Graph"

    kBooleanBox = "Boolean Box"

    kToggleButton = "Toggle Button"

    kToggleSwitch = "Toggle Switch"
    kVoltageView = "Voltage View"

    kPowerDistributionPanel = "PDP"

    kComboBoxChooser = "ComboBox Chooser"

    kSplitButtonChooser = "Split Button Chooser"

    kEncoder = "Encoder"

    kSpeedController = "Speed Controller"

    kCommand = "Command"

    kPIDCommand = "PID Command"

    kPIDController = "PID Controller"

    kAccelerometer = "Accelerometer"

    k3AxisAccelerometer = "3-Axis Accelerometer"

    kGyro = "Gyro"

    kRelay = "Relay"

    kDifferentialDrive = "Differential Drivebase"

    kMecanumDrive = "Mecanum Drivebase"

    kCameraStream = "Camera Stream"

    def getWidgetName(self):
        return self.value
