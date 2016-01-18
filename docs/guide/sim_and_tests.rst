
.. _sim_testing:

Simulation and Testing
======================

An important (but often neglected) part of developing your robot code is to
test it! Because we feel strongly about testing and simulation, the RobotPy
project provides tools to make those types of things easier through the 
`pyfrc <https://github.com/robotpy/pyfrc>`_ project.

Adding tests to your robot
--------------------------

pyfrc comes with builtin tests that you can add to your robot code that will
test basic functionality of most robots. As of pyfrc 2016.1.1, you can add
these tests to your robot by executing this:

.. code-block:: sh

    Windows:   py robot.py add-tests

    Linux/OSX: python3 robot.py add-tests

Customized tests
----------------

For more detailed information, check out the `pyfrc documentation <http://pyfrc.readthedocs.org>`_.

Next Steps
----------

Learn more about some :ref:`best_practices` when creating robot code. 
