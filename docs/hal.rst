hal package
===========

.. note:: Dealing with HAL is an advanced topic, and the documentation isn't
          as good as it could be. Be prepared to read the code directly!

Generally, RobotPy users don't need to interact much with the HAL package
except in simulation.

hal_data
--------

When running the robot code in simulation or in unit tests, anytime something
needs to interact with the hardware, typically functions in the HAL are called.
The simulated version of the HAL functions either set or get data to/from a
giant dictionary that we call the 'hal_data'.

To learn about the contents of the data in the dictionary, go to
``hal-sim/hal_impl/data.py`` and read the ``reset_hal_data`` function.

I2C/SPI Simulation Helpers
--------------------------

Interacting with custom I2C and SPI devices requires custom code. Because we
can't predict what kind of data your device will return when you ask for it,
the default simulation interfaces will discard all data written to the device,
and raise an exception when you try to read from the device. If you don't want
to receive these errors, then you need to do the following:

1. Create a simulation class that inherits from either :class:`.I2CSimBase` or
   :class:`.SPISimBase`, and override the needed functions.
2. Create an instance of the class, and pass it as the ``simPort`` argument
   of the I2C or SPI object constructor

For a working example of how to do this, look at the constructor of the
:class:`.ADXRS450_Gyro`, and its corresponding simulation interface
ADXRS450_Gyro_Sim found at ``hal-sim/hal_impl/spi_helpers.py``.

.. note:: The sim helper objects aren't installed on the roborio, so you 
          should only import them if a simulated hal is running. You can use
          the ``hal.isSimulation`` function to determine this.

.. autoclass:: hal_impl.i2c_helpers.I2CSimBase
   :members:
   :undoc-members:

.. autoclass:: hal_impl.spi_helpers.SPISimBase
   :members:
   :undoc-members: