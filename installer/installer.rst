
.. _robotpy_installer:

RobotPy Installer
=================

.. note:: This is not the RobotPy installation guide, see :ref:`getting_started`
          if you're looking for that!

Most FRC robots are not placed on networks that have access to the internet,
particularly at competition arenas. The RobotPy installer is designed for 
this type of 'two-phase' operation -- with individual steps for downloading
and installing packages separately.

As of 2015, the RobotPy installer now supports downloading external packages
from the python package repository (pypi) via pip, and installing those
packages onto the robot. We cannot make any guarantees about the quality of
external packages, so use them at your own risk.

.. note:: If your robot is on a network that has internet access, then you
          can manually install packages via opkg or pip. However, if you use
          the RobotPy installer to install packages, then you can easily
          reinstall them on your robot in the case you need to reimage it.

          If you choose to install packages manually via pip, keep in mind that
          when powered off, your RoboRIO does not keep track of the correct
          date, and as a result pip may fail with an SSL related error message.
          To set the date, you can either:

          * Set the date via the web interface 
          * You can login to your roboRIO via SSH, and set the date via the
            date command::

              date -s "2015-01-03 00:00:00"

Each of the commands supports various options, which you can read about by
invoking the --help command.

install-robotpy
---------------

::

	python3 installer.py install-robotpy

This will copy the appropriate RobotPy components to the robot, and install
them. If the components are already installed on the robot, then they will
be reinstalled.

download-robotpy
----------------

::

	python3 installer.py download-robotpy

This will update the cached RobotPy packages to the newest versions available.

download
--------

::

	python3 installer.py download PACKAGE [PACKAGE ..]

Specify python package(s) to download, similar to what you would pass the
'pip install' command. This command does not install files on the robot, and
must be executed from a computer with internet access.

You can run this command multiple times, and files will not be removed from 
the download cache.

You can also use a `requirements.txt` file to specify which packages should
be downloaded.

::

	python3 installer.py download -r requirements.txt

install
-------

::

	python3 installer.py install PACKAGE [PACKAGE ..]

Copies python packages over to the roboRIO, and installs them. If the
package already has been installed, it will be reinstalled.

You can also use a `requirements.txt` file to specify which packages should
be downloaded.

::

	python3 installer.py download -r requirements.txt

.. warning:: The 'install' command will only install packages that have been
             downloaded using the 'download' command, or packages that are
             on the robot's pypi cache.

.. warning:: If your robot does not have a python3 interpeter installed, this
             command will fail. Run the `install-robotpy` command first.
