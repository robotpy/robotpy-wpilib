.. _best_practices:

Best Practices
==============

This section has a selection of things that other teams have found to be good
things to keep in mind to build robot code that works consistently, and to 
eliminate possible failures.

.. contents::

If you have things to add to this section, feel free to submit a pull request!

Make sure you're running the latest version of RobotPy!
-------------------------------------------------------

Seriously. We try to fix bugs as we find them, and if you haven't updated 
recently, check to see if you're out of date! This is particularly true
this year.

Don't use the print statement/logger excessively
------------------------------------------------

Printing output can easily take up a large proportion of your robot code
CPU usage if you do it often enough. Try to limit the amount of things
that you print, and your robot will perform better.

Instead, you may want to use this pattern to only print once every half
second (or whatever arbitrary period)::

    # Put this in robotInit
    self.printTimer = wpilib.Timer()
    self.printTimer.start()

    .. 

    # Put this where you want to print
    if self.printTimer.hasPeriodPassed(0.5):
        self.logger.info("Something happened")


Remember, during a competition you can't actually see the output of Netconsole
(it gets blocked by the field network), so there's not much point in using
these except for diagnostics off the field. In a competition, disable it.


Don't die during the competition!
---------------------------------

If you've done any amount of programming in python, you'll notice that it's
really easy to crash your robot code -- all you need to do is mistype something
and BOOM you're done. When python encounters errors (or components such as
WPILib or HAL), then what happens is an exception is raised.

.. note:: If you don't know what exceptions are and how to deal with them, you
          should read `this <https://docs.python.org/2/tutorial/errors.html>`_

There's a lot of things that can cause your program to crash, and generally
the best way to make sure that it doesn't crash is **test your code**. RobotPy
provides some great tools to allow you to simulate your code, and to write
unit tests that make sure your code actually works. Whenever you deploy your
code using pyfrc, it tries to run your robot code's tests -- and this is to
try and prevent you from uploading code that will fail on the robot.

However, invariably even with all of the testing you do, something will go
wrong during that really critical match, and your code will crash. No fun.
Luckily, there's a good technique you can use to help prevent that!

What you need to do is set up a generic exception handler that will catch
exceptions, and then if you detect that the FMS is attached (which is only
true when you're in an actual match), just continue on instead of crashing
the code.

.. note:: Most of the time when you write code, you never want to create
          generic exception handlers, but you should try to catch specific
          exceptions. However, this is a special case and we actually do
          want to catch all exceptions.

Here's what I mean::

    try:
        # some code goes here
    except:
        if not self.isFmsAttached():
            raise

What this does is run some code, and if an exception occurs in that code
block, and the FMS is connected, then execution just continues and
hopefully everything continues working. However (and this is important),
if the FMS is not  attached (like in a practice match), then the ``raise``
keyword tells python to raise the exception anyways, which will most likely
crash your robot. But this is good in practice mode -- if your driver
station is attached, the error and a stack trace should show up in the
driver station log, so you can debug the problem.

Now, a naive implementation would just put all of your code inside of a
single exception handler -- but that's a bad idea. What we're trying to
do is make sure that failures in a single part of your robot don't cause
the rest of your robot code to not function. What we generally try to do
is put each logical piece of code in the main robot loop (teleopPeriodic)
in its own exception handler, so that failures are localized to specific
subsystems of the robot.

With these thoughts in mind, here's an example of what I mean::

    def teleopPeriodic(self):

        try:
            if self.joystick.getTrigger():
                self.arm.raise_arm()
        except:
            if not self.isFmsAttached():
                raise

        try:
            if self.joystick.getRawButton(2):
                self.ball_intake.()
        except:
            if not self.isFmsAttached():
                raise

        # and so on... 

        try:
            self.robot_drive.arcadeDrive(self.joystick)
        except:
            if not self.isFmsAttached():
                raise

.. note:: In particular, I always recommend making sure that the call to your
          robot's drive function is in it's own exception handler, so even if
          everything else in the robot dies, at least you can still drive
          around.

Next Steps
==========

Next we'll discuss some topic that will be decided upon in the future, if someone writes more documentation here. Until then, remember that the FIRST documentation and our example programs are great resources to learn more about programming with WPILib.
