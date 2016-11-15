
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
    
    Windows:   py robot.py deploy

    Linux/OSX: python3 robot.py deploy

Note that when you run this command like that, you won't get any feedback from the robot whether your code actually worked or not. If you want to see the feedback from your robot, a really useful option is ``--nc``. This will cause the deploy command to show your program's console output, by launching a netconsole listener.

.. code-block:: sh

    Windows:   py robot.py deploy --nc
    
    Linux/OSX: python3 robot.py deploy --nc

You can watch your robot code's output (and see any problems) by using the netconsole program (you can either use NI's tool, or `pynetconsole <https://github.com/robotpy/pynetconsole>`_. You can use netconsole and the normal FRC tools to interact with the running robot code.

If you're having problems deploying code to the robot, check out the troubleshooting section at http://pyfrc.readthedocs.org/en/latest/deploy.html

On the robot (manual)
---------------------

If you don't have (or don't want) to install pyfrc, running code manually is pretty simple too. 

1. Make sure you have RobotPy installed on the robot
2. Use scp or sftp (Filezilla is a great GUI product to use for this) to copy your robot code to the roboRIO
3. ssh into the roboRIO, and run your robot code manually

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

The next section discusses a very important part of writing robot code -- :ref:`sim_testing`.




