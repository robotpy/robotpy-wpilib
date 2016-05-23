
.. _getting_started:

Getting Started
===============

Welcome to RobotPy! RobotPy is a community of FIRST mentors and students
dedicated to developing python-related projects for the FIRST Robotics
Competition.

RobotPy WPILib is a set of libraries that are used on your roboRIO to
enable you to use Python as your main programming language for FIRST Robotics
robot development. It includes support for all components that are supported by
WPILib's Java implementation. The following instructions tell you how to
install RobotPy on your robot.

If you want to run your python code on your computer (of course you do!),
then you need to install our python development support tools, which is a
separate project of ours called pyfrc. For more information, check out the
`pyfrc documentation site <http://pyfrc.readthedocs.org/>`_.


.. note:: Once you've got robotpy installed on your robot, check out 
          :ref:`anatomy` to learn how to write robot code using python and
          RobotPy.


Automated installation
----------------------

RobotPy is truly cross platform, and can be installed from Windows, most Linux
distributions, and from Mac OSX also. Here's how you do it:

* `Download RobotPy from github <https://github.com/robotpy/robotpy-wpilib/releases>`_
* `Make sure Python 3.4 is installed <https://www.python.org/downloads/>`_

Unzip the RobotPy zipfile somewhere on your computer (not on the RoboRIO),
and there should be an installer.py there. Open up a command line, change
directory to the installer location, and run this::

	Windows:   py installer.py install-robotpy
	
	Linux/OSX: python3 installer.py install-robotpy

It will ask you a few questions, and copy the right files over to your robot
and set things up for you. 

Next, you'll want to create some code (or maybe use one of our examples),
and upload it to your robot! Refer to our :ref:`programmers_guide` for more
information.

Upgrading
~~~~~~~~~

From the same directory that you unzipped previously, you can run the same 
installer script to upgrade your robotpy installation. You need to do it in
two phases, one while connected to the internet to download the new release,
and one while connected to the Robot's network.

When connected to the internet::

	Windows:   py installer.py download-robotpy
	
	Linux/OSX: python3 installer.py download-robotpy
	
Then connect to the Robot's network::

	Windows:   py installer.py install-robotpy
	
	Linux/OSX: python3 installer.py install-robotpy

If you want to use a beta version of RobotPy (if available, you can add the 
--pre argument to the download/install command listed above.


Manual installation (release)
-----------------------------

.. warning:: This isn't recommended, so you're on your own if you go this route.
             
If you really want to do this, it's not so bad, but then you lose out on
the benefits of the automated installer -- in particular, this method requires
internet access to install the files on the RoboRIO in case you need to reimage
your RoboRIO.

* Connect your RoboRIO to the internet
* SSH in, and copy the following to /etc/opkg/robotpy.conf::

    src/gz robotpy http://www.tortall.net/~robotpy/feeds/2014
	
* Run this::

    opkg install python3
	
* Then run this::

    pip3 install pynivision robotpy-hal-roborio wpilib

.. note:: When powered off, your RoboRIO does not keep track of the correct
          date, and as a result pip may fail with an SSL related error message.
          To set the date, you can either:

          * Set the date via the web interface 
          * You can login to your roboRIO via SSH, and set the date via the
            date command::

          		date -s "2015-01-03 00:00:00"

Upgrading requires you to run the same commands, but with the appropriate
flags set to tell pip3/opkg to upgrade the packages for you.

Manual Installation (developer)
-------------------------------

.. warning:: These instructions are only intended for those users wanting to deploy
             a custom modified version of the RobotPy WPILib source code

.. note:: These instructions assume you have cloned the git repository for robotpy-wpilib,
          and made changes in that repository checkout.

First, install python on the RoboRIO using one of the two methods above. To deploy
your changes, you can run ``devtools/build_and_deploy.sh`` from the root of the
git repository.
