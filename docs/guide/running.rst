
.. _running_robot_code:

Running Robot Code
==================

Now that you've created your first Python robot program, you probably want to know how to run the code.

On the robot (using pyfrc)
--------------------------

The easiest way to install code on the robot is to use pyfrc. 

1. Make sure you have RobotPy installed on the robot
2. Make sure you have pyfrc installed (`see the installation guide <http://pyfrc.readthedocs.org/en/latest/install.html>`_).
3. Once that is done, you can just run the following command and it will upload the code and start it immediately.

:: 
    
    Windows:   py robot.py upload

    Linux/OSX: python3 robot.py upload

You can use netconsole and the normal FRC tools to interact with the running robot code.

On the robot (manual)
---------------------

If you don't have (or don't want) to install pyfrc, running code manually is pretty simple too. 

1. Make sure you have RobotPy installed on the robot
2. Use scp or sftp (Filezilla is a great GUI product to use for this) to copy your robot code to the RoboRIO
3. ssh into the RoboRIO, and run your robot code manually

::

	python3 robot.py run 

Your driver station should be able to connect to your code, and it will be able to operate your robot!

.. note:: This is good for running experimental code, but it won't start the code when the robot starts up. Use pyfrc to do that.


On your computer
----------------

Once installed, pyfrc provides a number of commands to interact with your robot code. For example, to launch the tk-based simulator, run the following command on your code::

    Windows:   py robot.py sim
    
    Linux/OSX: python3 robot.py sim

Check out the pyfrc documentation for `more usage details <http://pyfrc.readthedocs.org/en/latest/usage.html>`_.

Gazebo simulation
-----------------

This is currently experimental, and will be updated in the coming weeks. If you want to play with it now (and help us fix the bugs!), check out the `robotpy-frcsim github repository <https://github.com/robotpy/robotpy-frcsim>`_.


Next steps
----------

Next we'll discuss some topic that will be decided upon in the future, if someone writes more documentation here. Until then, remember that the FIRST documentation and our example programs are great resources to learn more about programming with WPILib.




