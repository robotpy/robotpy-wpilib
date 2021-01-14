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
