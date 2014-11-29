Implementation Details
======================

This page contains various design/implementation notes that are useful to
people that are peering at the internals of WPILib/HAL. We will try to 
keep this document up to date... 

Design Goals
------------

The python implementation of WPILib/HAL is derived from the Java implementation
of WPILib. In particular, we strive to keep the python implementation of WPILib
as close to the spirit of the original WPILib java libraries as we can, only
adding language-specific features where it makes sense.

Things that you won't find in the original WPILib can be found in the _impl
package.

If you have a suggestion for things to add to WPILib, we suggest adding it to
the `robotpy_ext <https://github.com/robotpy/robotpy-wpilib-utilities>`_ package,
which is a separate package for "high quality code of things that should be in
WPILib, but aren't". This package is installed by the RobotPy installer by 
default.

HAL Loading
-----------

Currently, the HAL is split into two python packages:

* hal - Provided by the robotpy-hal-base package
* hal_impl - Provided by either robotpy-hal-roborio or robotpy-hal-sim

You can only have a single hal_impl package installed in a particular python
installation.

The :mod:`hal` package provides the definition of the functions and various
types & required constants.

The :mod:`hal_impl` package provides the actual implementation of the HAL
functions, or links them to a shared DLL via ctypes. 


Adding options to robot.py
--------------------------

When :func:`wpilib.run` is called, that function determines available commands
that can be run, and parses command line arguments to pass to the commands.
Examples of commands include:

* Running the robot code
* Running the robot code, connected to a simulator
* Running unit tests on the robot code
* And lots more!

python setuptools has a feature that allows you to extend the commands available
to robot.py without needing to modify WPILib's code. To add your own command,
do the following:

* Define a setuptools entrypoint in your package's setup.py (see below)
* The entrypoint name is the command to add
* The entrypoint must point at an object that has the following properties:
    * Must have a docstring (shown when --help is given)
    * Constructor must take a single argument (it is an argparse parser which options can be added to)
    * Must have a 'run' function which takes two arguments: options, and robot_class

If your command's run function is called, it is your command's responsibility
to execute the robot code (if that is desired). This sample command 
demonstrates how to do this::

    class SampleCommand:
        '''Help text shown to user'''

        def __init__(self, parser):
            pass

        def run(self, options, robot_class):
            # runs the robot code main loop
            robot_class.main(robot_class)

To register your command as a robotpy extension, you must add the following
to your setup.py setup() invocation::

    from setuptools import setup

    setup(
          ...
          entry_points={'robot_py': ['name_of_command = package.module:CommandClassName']},
          ... 
          )
