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
    * Must have a 'run' function which takes two arguments: options, and robot_class. It must
      also take arbitrary keyword arguments via the **kwargs mechanism. If it receives arguments
      that it does not recognize, the entry point must ignore any such options.

If your command's run function is called, it is your command's responsibility
to execute the robot code (if that is desired). This sample command 
demonstrates how to do this::

    class SampleCommand:
        '''Help text shown to user'''

        def __init__(self, parser):
            pass

        def run(self, options, robot_class, **static_options):
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

Updating RobotPy source code to match WPILib
--------------------------------------------

Every year, the WPILib team makes improvements to WPILib, so RobotPy needs to be
updated to maintain compatibility. While this is largely a manual process, we
use a tool called `git-source-track <https://github.com/virtuald/git-source-track>`_
to assist with this process.

.. note:: git-source-track only works on Linux/OSX at this time. If you're
          interested in helping with the porting process and you use Windows,
          file a github issue and we'll try to help you out.

Using git-source-track
~~~~~~~~~~~~~~~~~~~~~~

First, you need to checkout the git repo for `allwpilib <https://github.com/wpilibsuite/allwpilib>`_
and the RobotPy WPILib next to each other in the same directory like so:

::
    
    allwpilib/
    robotpy-wpilib/

The way git-source-track works is it looks for a comment in the header of each
tracked file that looks like this::
    
    # validated: 2015-12-24 DS 6d854af athena/java/edu/wpi/first/wpilibj/Compressor.java
    
This stores when the file was validated to match the original source, initials
of the person that did the validation, what commit it was validated against, and
the path to the original source file.

Finding differences
~~~~~~~~~~~~~~~~~~~

From the `robotpy-wpilib` directory, you can run ``git source-track`` and it
will output all of the configured files and their status. The status codes
include:

* ``OK``: File is up to date, no changes required
* ``OLD``: The tracked file has been updated, ```git source-track diff FILENAME`` can
  be used to show all of the git log messages and associated diffs.
* ``ERR``: The tracked file has moved or has been deleted
* ``--``: The file is not currently being tracked

Sometimes, commits are added to WPILib which only change comments, formatting,
or mass file renames -- these don't change the semantic content of the file,
so we can ignore those commits. When identified, those commits should be added
to ``devtools/exclude_commits``.

Looking at differences
~~~~~~~~~~~~~~~~~~~~~~

Once you've identified a file that needs to be updated, then you can run::
    
    git source-track diff FILENAME
    
This will output a verbose git log command that will show associated commit
messages and the diff output associated with that commit for that specific file.
Note that it will only show the change for that specific file, it will
not show changes for other files (use ``git log -p COMMITHASH`` in the 
original source directory if you want to see other changes).

After running ``git source-track diff`` it will ask you if you want to validate
the file. If no python-significant changes have been made, then you can answer
'y' and the validation header will be updated.

Adding new files
~~~~~~~~~~~~~~~~

Unfortunately, git-source-track doesn't currently have a mechanism that allows
it to identify new files that need to be ported. We need to do that manually.

Converting javadocs to docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is an HTML page in devtools called ``convert_javadoc.html`` that you can
use. The way it works is you copy a Java docstring in the top box (you can also
paste in a  function definition too) and it will output a python docstring in
the bottom box. When adding new APIs that have documentation, this tool is
invaluable -- feel free to improve it though!

Dealing with RobotPy-specific files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We don't need to track those files; ``git source-track set-notrack FILENAME``
takes care of it.

After you finish porting the changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've finished making the appropriate changes to the python code, then
you should update the validation header in the source file. Thankfully,
there's a command to do this::
    
    git source-track set-valid FILENAME
    
It will store the current date and the tracked git commit.

Additionally, if you answer 'y' after running ``git source-track diff FILENAME``,
then it will update the validation header in the file.

HAL Changes
~~~~~~~~~~~

If there are changes to the HAL, we have some scripts that should be able to
help out here.

* ``devtools/hal_fix.sh``: This detects errors in the HAL,
  and if you pass it the ``--stubs`` argument it can print out the correct 
  HAL definitions or a python stub. Use ``--help`` for more information.


