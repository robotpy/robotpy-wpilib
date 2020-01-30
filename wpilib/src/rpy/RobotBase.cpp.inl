
auto logger = py::module::import("logging").attr("getLogger")("robot");
cls_RobotBase.attr("logger") = logger;

cls_RobotBase
    .def_static(
        "main",
        [](py::object robot_cls) -> py::object {
          auto start = py::module::import("wpilib._impl.start");
          auto starter = start.attr("RobotStarter")();
          return starter.attr("run")(robot_cls);
        },
        py::arg("robot_cls"), "Starting point for the application")
    .def(
        "getControlState",
        [](RobotBase *that) -> py::tuple {
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
        [](RobotBase *that) -> bool {
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
        [](RobotBase *that) -> bool {
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
