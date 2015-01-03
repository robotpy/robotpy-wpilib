
.. _getting_started:

Getting Started
===============

.. note:: These instructions tell you how to install RobotPy on your robot. Once you've
		  got it installed there, check out :ref:`anatomy` to learn how to write robot
		  code using python and RobotPy.


Automated installation
----------------------

RobotPy is truly cross platform, and can be installed from Windows, most Linux
distributions, and from Mac OSX also. Here's how you do it:

* `Download RobotPy from github <https://github.com/robotpy/robotpy-wpilib/releases>`_
* `Make sure Python 3.4 is installed <https://www.python.org/downloads/>`_

Unzip the RobotPy zipfile somewhere, and there should be an installer.py
there. Open up a command line, change directory to the installer location,
and run this::

	Windows:   py installer.py install-robotpy
	
	Linux/OSX: python3 installer.py install-robotpy

It will ask you a few questions, and copy the right files over to your robot
and set things up for you. 

Next, you'll want to create some code (or maybe use one of our examples),
and upload it to your robot! Refer to our :ref:`programmers-guide` for more
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


Manual installation
-------------------

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

	pip3 install robotpy-hal-roborio wpilib
	
Upgrading requires you to run the same commands, but with the appropriate
flags set to tell pip3/opkg to upgrade the packages for you.

