
.. _wpilib_api:

WPILib API
----------

The WPI Robotics library (WPILib) is a set of classes that interfaces to the hardware in the FRC
control system and your robot. There are classes to handle sensors, motors, the driver
station, and a number of other utility functions like timing and field management.
The library is designed to:

- Deal with all the low level interfacing to these components so you can concentrate on
  solving this year's "robot problem". This is a philosophical decision to let you focus
  on the higher-level design of your robot rather than deal with the details of the
  processor and the operating system.
- Understand everything at all levels by making the full source code of the library
  available. You can study (and modify) the algorithms used by the gyro class for
  oversampling and integration of the input signal or just ask the class for the current
  robot heading. You can work at any level.


.. toctree::

    wpilib
    wpilib.buttons
    wpilib.command
    wpilib.drive
    wpilib.interfaces
    wpilib.shuffleboard
    
    hal
