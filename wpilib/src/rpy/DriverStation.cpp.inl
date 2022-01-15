cls_DriverStation
    .def(
        "getControlState",
        [](DriverStation *that) -> std::tuple<bool, bool, bool> {
          py::gil_scoped_release release;
          return rpy::GetControlState();
        },
        "More efficient way to determine what state the robot is in.\n"
        "\n"
        ":returns: booleans representing enabled, isautonomous, istest\n"
        "\n"
        ".. versionadded:: 2019.2.1\n"
        "\n"
        ".. note:: This function only exists in RobotPy\n");
