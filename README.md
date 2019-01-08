RobotPy WPILib
==============

[![Build Status](https://travis-ci.org/robotpy/robotpy-wpilib.svg?branch=master)](https://travis-ci.org/robotpy/robotpy-wpilib)

This repository contains the source code for a 100% python implementation of WPILib, 
the library used to interface with hardware for the FIRST Robotics Competition. 
Teams can use this library to write their robot code in Python, a powerful dynamic
programming language.

**Note**: RobotPy is a community project and is not officially supported by
FIRST. Please see the [FAQ](http://robotpy.github.io/faq/) for more information.

Documentation
=============

All RobotPy documentation can be found at http://robotpy.readthedocs.org

Installation
============

Installation instructions can be found in the [RobotPy documentation](http://robotpy.readthedocs.org/en/latest/getting_started.html)

Packages
========

* `wpilib` - python implementation of WPILib
* `hal-base` - Contains base functionality the wpilib package uses to interface with the HAL
* `hal-roborio` - Functionality to allow hal-base to interface with the HAL C library via ctypes
* `hal-sim` - All HAL functions write to a data structure that can be used for simulation and testing

License
=======

See [LICENSE.txt](wpilib/LICENSE.txt)

Contributors
============

Peter Johnson (@PeterJohnson, FRC Team 294) & Dustin Spicuzza (@virtuald,
FRC Team 1418/2423) are the primary maintainers of RobotPy.

Christian Balcom (@computer-whisperer, FRC Team 4819) has done a significant
amount of work on the pure python port of WPILib, and various useful tooling.

Other contributors include:

* Sam Rosenblum (@sarosenb, FRC Team 2423)


