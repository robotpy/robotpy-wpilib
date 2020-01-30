cls_DriverStation
    .def_static(
        "reportError",
        [](py::str error, py::bool_ printTrace) {
          auto start_module = py::module::import("wpilib._impl.report_error");
          return start_module.attr("report_error")(true, 1, error, printTrace);
        },
        py::arg("error"), py::arg("printTrace"),

        "Report error to Driver Station, and also prints error to "
        "`sys.stderr`.\n"
        "Optionally appends stack trace to error message.\n"
        "\n"
        ":param printTrace: If True, append stack trace to error string\n"
        "\n"
        "The error is also printed to the program console.")
    .def_static(
        "reportWarning",
        [](py::str error, py::bool_ printTrace) {
          auto start_module = py::module::import("wpilib._impl.report_error");
          return start_module.attr("report_error")(false, 1, error, printTrace);
        },
        py::arg("error"), py::arg("printTrace"),

        "Report warning to Driver Station, and also prints error to "
        "`sys.stderr`.\n"
        "Optionally appends stack trace to error message.\n"
        "\n"
        ":param printTrace: If True, append stack trace to error string\n"
        "\n"
        "The error is also printed to the program console.")
    .def(
        "getControlState",
        [](DriverStation *that) -> py::tuple {
          py::tuple retval(3);

          HAL_ControlWord controlWord;

          {
            py::gil_scoped_release release;
            HAL_GetControlWord(&controlWord);
          }

          retval[0] = py::bool_(controlWord.enabled != 0 &&
                                controlWord.dsAttached != 0);
          retval[1] = py::bool_(controlWord.autonomous != 0);
          retval[2] = py::bool_(controlWord.test != 0);
          return retval;
        },
        "More efficient way to determine what state the robot is in.\n"
        "\n"
        ":returns: booleans representing enabled, isautonomous, istest\n"
        "\n"
        ".. versionadded:: 2019.2.1\n"
        "\n"
        ".. note:: This function only exists in RobotPy\n")
    .def(
        "isAutonomousEnabled",
        [](DriverStation *that) -> bool {
          py::gil_scoped_release release;
          HAL_ControlWord controlWord;
          HAL_GetControlWord(&controlWord);

          return controlWord.autonomous != 0 &&
              controlWord.enabled != 0 &&
              controlWord.dsAttached != 0;
        },
        "Equivalent to calling ``isAutonomous() and isEnabled()`` but\n"
        "more efficient.\n"
        "\n"
        ":returns: True if the robot is in autonomous mode and is enabled,\n"
        "    False otherwise.\n"
        "\n"
        ".. versionadded:: 2019.2.1\n"
        "\n"
        ".. note:: This function only exists in RobotPy\n")
    .def(
        "isOperatorControlEnabled",
        [](DriverStation *that) -> bool {
          py::gil_scoped_release release;
          HAL_ControlWord controlWord;
          HAL_GetControlWord(&controlWord);

          return !(controlWord.autonomous != 0 || controlWord.test != 0) &&
              controlWord.enabled != 0 && controlWord.dsAttached != 0;
        },
        "Equivalent to calling ``isOperatorControl() and isEnabled()`` but\n"
        "more efficient.\n"
        "\n"
        ":returns: True if the robot is in operator-controlled mode and is "
        "enabled,\n"
        "    False otherwise.\n"
        "\n"
        ".. versionadded:: 2019.2.1\n"
        "\n"
        ".. note:: This function only exists in RobotPy\n");
