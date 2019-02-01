# validated: 2019-01-10 DV 01d13220660c edu/wpi/first/wpilibj/shuffleboard/BuiltInWidgets.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import enum


class BuiltInWidgets(enum.Enum):
    """The types of the widgets bundled with Shuffleboard.

    For example, setting a number to be displayed with a slider::

        example_entry = (
            Shuffleboard.getTab("My Tab")
            .add("My Number", 0)
            .withWidget(BuiltInWidgets.kNumberSlider)
            .withProperties({"min": 0, "max": 1})
            .getEntry()
        )

    Each value in this enum goes into detail on what data types that
    widget can support, as well as the custom properties that widget uses.
    """

    #: Displays a value with a simple text field.
    #:
    #: Supported types:
    #:
    #: - String
    #: - Number
    #: - Boolean
    #:
    #: This widget has no custom properties.
    kTextView = "Text View"

    #: Displays a number with a controllable slider.
    #:
    #: Supported types:
    #:
    #: - Number
    #:
    #: Custom properties:
    #:
    #: .. csv-table::
    #:    :header: Name, Type, Default Value, Notes
    #:    :widths: auto
    #:
    #:    Min,             Number, -1.0,   The minimum value of the slider
    #:    Max,             Number, 1.0,    The maximum value of the slider
    #:    Block increment, Number, 0.0625, How much to move the slider by with the arrow keys
    kNumberSlider = "Number Slider"

    #: Displays a number with a view-only bar.
    #:
    #: Supported types:
    #:
    #: - Number
    #:
    #: Custom properties:
    #:
    #: ======  ======  =============  ====================================
    #: Name    Type    Default Value  Notes
    #: ======  ======  =============  ====================================
    #: Min     Number  -1.0           The minimum value of the bar
    #: Max     Number  1.0            The maximum value of the bar
    #: Center  Number  0              The center ("zero") value of the bar
    #: ======  ======  =============  ====================================
    kNumberBar = "Number Bar"

    #: Displays a number with a view-only dial.
    #: Displayed values are rounded to the nearest integer.
    #:
    #: Supported types:
    #:
    #: - Number
    #:
    #: Custom properties:
    #:
    #: .. list-table::
    #:    :widths: auto
    #:    :header-rows: 1
    #:
    #:    * - Name
    #:      - Type
    #:      - Default Value
    #:      - Notes
    #:    * - Min
    #:      - Number
    #:      - 0
    #:      - The minimum value of the dial
    #:    * - Max
    #:      - Number
    #:      - 100
    #:      - The maximum value of the dial
    #:    * - Show value
    #:      - Boolean
    #:      - true
    #:      - Whether or not to show the value as text
    kDial = "Simple Dial"

    #: Displays a number with a graph.
    #:
    #: .. note::
    #:    Graphs can be taxing on the computer running the dashboard.
    #:    Keep the number of visible data points to a minimum.
    #:    Making the widget smaller also helps with performance,
    #:    but may cause the graph to become difficult to read.
    #:
    #: Supported types:
    #:
    #: - Number
    #: - Number array
    #:
    #: Custom properties:
    #:
    #: ============ ====== ============= =====================================================
    #: Name         Type   Default Value Notes
    #: ============ ====== ============= =====================================================
    #: Visible time Number 30            How long, in seconds, should past data be visible for
    #: ============ ====== ============= =====================================================
    kGraph = "Graph"

    #: Displays a boolean value as a large colored box.
    #:
    #: Supported types:
    #:
    #: - Boolean
    #:
    #: Custom properties:
    #:
    #: ================ ===== ============= ===============================================================================
    #: Name             Type  Default Value Notes
    #: ================ ===== ============= ===============================================================================
    #: Color when true  Color "green"       Can be specified as a string (``"#00FF00"``) or a rgba integer (``0x00FF0000``)
    #: Color when false Color "red"         Can be specified as a string or a number
    #: ================ ===== ============= ===============================================================================
    kBooleanBox = "Boolean Box"

    #: Displays a boolean with a large interactive toggle button.
    #:
    #: Supported types:
    #:
    #: - Boolean
    #:
    #: This widget has no custom properties.
    kToggleButton = "Toggle Button"

    #: Displays a boolean with a fixed-size toggle switch.
    #:
    #: Supported types:
    #:
    #: - Boolean
    #:
    #: This widget has no custom properties.
    kToggleSwitch = "Toggle Switch"

    #: Displays an analog input or a raw number with a number bar.
    #:
    #: Supported types:
    #:
    #: - Number
    #: - :class:`.AnalogInput`
    #:
    #: Custom properties:
    #:
    #: ==================== ====== ============= =================================================================
    #: Name                 Type   Default Value Notes
    #: ==================== ====== ============= =================================================================
    #: Min                  Number 0             The minimum value of the bar
    #: Max                  Number 5             The maximum value of the bar
    #: Center               Number 0             The center ("zero") value of the bar
    #: Orientation          String "HORIZONTAL"  The orientation of the bar. One of ``["HORIZONTAL", "VERTICAL"]``
    #: Number of tick marks Number 5             The number of discrete ticks on the bar
    #: ==================== ====== ============= =================================================================
    kVoltageView = "Voltage View"

    #: Displays a :class:`.PowerDistributionPanel`.
    #:
    #: Supported types:
    #:
    #: - :class:`.PowerDistributionPanel`
    #:
    #: =============================== ======= ============= ======================================================
    #: Name                            Type    Default Value Notes
    #: =============================== ======= ============= ======================================================
    #: Show voltage and current values Boolean True          Whether or not to display the voltage and current draw
    #: =============================== ======= ============= ======================================================
    kPowerDistributionPanel = "PDP"

    #: Displays a :class:`.SendableChooser` with a dropdown combo box with a list of options.
    #:
    #: Supported types:
    #:
    #: - :class:`.SendableChooser`
    #:
    #: This widget has no custom properties.
    kComboBoxChooser = "ComboBox Chooser"

    #: Displays a :class:`.SendableChooser` with a dropdown combo box with a toggle button for each available option.
    #:
    #: Supported types:
    #:
    #: - :class:`.SendableChooser`
    #:
    #: This widget has no custom properties.
    kSplitButtonChooser = "Split Button Chooser"

    #: Displays an :class:`.Encoder` displaying its speed, total travelled distance, and its distance per tick.
    #:
    #: Supported types:
    #:
    #: - :class:`.Encoder`
    #:
    #: This widget has no custom properties.
    kEncoder = "Encoder"

    #: Displays a :class:`.SpeedController`.
    #: The speed controller will be controllable from the dashboard when
    #: test mode is enabled, but will otherwise be view-only.
    #:
    #: Supported types:
    #:
    #: - :class:`.PWMSpeedController`
    #: - :class:`.DMC60`
    #: - :class:`.Jaguar`
    #: - :class:`.PWMTalonSRX`
    #: - :class:`.PWMVictorSPX`
    #: - :class:`.SD540`
    #: - :class:`.Spark`
    #: - :class:`.Talon`
    #: - :class:`.Victor`
    #: - :class:`.VictorSP`
    #: - :class:`.SpeedControllerGroup`
    #:
    #: Custom properties:
    #:
    #: =========== ====== ============= =====================================
    #: Name        Type   Default Value Notes
    #: =========== ====== ============= =====================================
    #: Orientation String "HORIZONTAL"  One of ``["HORIZONTAL", "VERTICAL"]``
    #: =========== ====== ============= =====================================
    kSpeedController = "Speed Controller"

    #: Displays a command with a toggle button.
    #: Pressing the button will start the command, and the
    #: button will automatically release when the command completes.
    #:
    #: Supported types:
    #:
    #: - :class:`wpilib.command.command.Command`
    #: - :class:`wpilib.command.commandgroup.CommandGroup`
    #: - Any custom subclass of ``Command`` or ``CommandGroup``
    #:
    #: This widget has no custom properties.
    kCommand = "Command"

    #: Displays a PID command with a checkbox and an editor for the PIDF constants.
    #: Selecting the checkbox will start the command, and the checkbox will
    #: automatically deselect when the command completes.
    #:
    #: Supported types:
    #:
    #: - :class:`wpilib.command.pidcommand.PIDCommand`
    #: - Any custom subclass of ``PIDCommand``
    #:
    #: This widget has no custom properties.
    kPIDCommand = "PID Command"

    #: Displays a PID controller with an editor for the PIDF constants and
    #: a toggle switch for enabling and disabling the controller.
    #:
    #: Supported types:
    #:
    #: - :class:`.PIDController`
    #:
    #: This widget has no custom properties.
    kPIDController = "PID Controller"

    #: Displays an accelerometer with a number bar displaying the magnitude of the acceleration and
    #: text displaying the exact value.
    #:
    #: Supported types:
    #:
    #: - :class:`.AnalogAccelerometer`
    #:
    #: Custom properties:
    #:
    #: =============== ======= ============= ===================================================
    #: Name            Type    Default Value Notes
    #: =============== ======= ============= ===================================================
    #: Min             Number  -1            The minimum acceleration value to display
    #: Max             Number  1             The maximum acceleration value to display
    #: Show text       Boolean True          Show or hide the acceleration values
    #: Precision       Number  2             How many numbers to display after the decimal point
    #: Show tick marks Boolean False         Show or hide the tick marks on the number bars
    #: =============== ======= ============= ===================================================
    kAccelerometer = "Accelerometer"

    #: Displays a 3-axis accelerometer with a number bar for each axis' accleration.
    #:
    #: Supported types:
    #:
    #: - :class:`.ADXL345_I2C`
    #: - :class:`.ADXL345_SPI`
    #: - :class:`.ADXL362`
    #:
    #: Custom properties:
    #:
    #: =============== ============================= ============= ===================================================
    #: Name            Type                          Default Value Notes
    #: =============== ============================= ============= ===================================================
    #: Range           :class:`.Accelerometer.Range` k16G          The accelerometer range
    #: Show value      Boolean                       True          Show or hide the acceleration values
    #: Precision       Number                        2             How many numbers to display after the decimal point
    #: Show tick marks Boolean                       False         Show or hide the tick marks on the number bars
    #: =============== ============================= ============= ===================================================
    k3AxisAccelerometer = "3-Axis Accelerometer"

    #: Displays a gyro with a dial from 0 to 360 degrees.
    #:
    #: Supported types:
    #:
    #: - :class:`.ADXRS450_Gyro`
    #: - :class:`.AnalogGyro`
    #: - Any custom subclass of ``GyroBase`` (such as a MXP gyro)
    #:
    #: Custom properties:
    #:
    #: =================== ======= ============= =============================================
    #: Name                Type    Default Value Notes
    #: =================== ======= ============= =============================================
    #: Major tick spacing  Number  45            Degrees
    #: Starting angle      Number  180           How far to rotate the entire dial, in degrees
    #: Show tick mark ring Boolean True
    #: =================== ======= ============= =============================================
    kGyro = "Gyro"

    #: Displays a relay with toggle buttons for each supported mode (off, on, forward, reverse).
    #:
    #: Supported types:
    #:
    #: - :class:`.Relay`
    #:
    #: This widget has no custom properties.
    kRelay = "Relay"

    #: Displays a differential drive with a widget that displays the speed of each side
    #: of the drivebase and a vector for the direction and rotation of the drivebase.
    #: The widget will be controllable if the robot is in test mode.
    #:
    #: Supported types:
    #:
    #: - :class:`wpilib.drive.differentialdrive.DifferentialDrive`
    #:
    #: Custom properties:
    #:
    #: ===================== ======= ============= ===============================
    #: Name                  Type    Default Value Notes
    #: ===================== ======= ============= ===============================
    #: Number of wheels      Number  4             Must be a positive even integer
    #: Wheel diameter        Number  80            Pixels
    #: Show velocity vectors Boolean True
    #: ===================== ======= ============= ===============================
    kDifferentialDrive = "Differential Drivebase"

    #: Displays a mecanum drive with a widget that displays the speed of each wheel,
    #: and vectors for the direction and rotation of the drivebase.
    #: The widget will be controllable if the robot is in test mode.
    #:
    #: Supported types:
    #:
    #: - :class:`wpilib.drive.mecanumdrive.MecanumDrive`
    #:
    #: Custom properties:
    #:
    #: ===================== ======= ============= =====
    #: Name                  Type    Default Value Notes
    #: ===================== ======= ============= =====
    #: Show velocity vectors Boolean True
    #: ===================== ======= ============= =====
    kMecanumDrive = "Mecanum Drivebase"

    #: Displays a camera stream.
    #:
    #: Supported types:
    #:
    #: - TODO
    #:
    #: Custom properties:
    #:
    #: =============== ======= ============= =====================================================================================
    #: Name            Type    Default Value Notes
    #: =============== ======= ============= =====================================================================================
    #: Show crosshair  Boolean True          Show or hide a crosshair on the image
    #: Crosshair color Color   "white"       Can be a string or a rgba integer
    #: Show controls   Boolean True          Show or hide the stream controls
    #: Rotation        String  "NONE"        Rotates the displayed image. One of ``["NONE", "QUARTER_CW", "QUARTER_CCW", "HALF"]``
    #: =============== ======= ============= =====================================================================================
    kCameraStream = "Camera Stream"
