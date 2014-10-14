#!/usr/bin/env python3

from setuptools import setup

setup(
    name='roborio-hal',
    version='1.0',
    description='WPILib HAL layer for roboRIO platform',
    author='Peter Johnson, Dustin Spicuzza',
    author_email='johnson.peter@gmail.com',
    url='https://github.com/robotpy',
    keywords='frc first robotics hal can',
    py_modules=['hal', 'frccan'],
    )
