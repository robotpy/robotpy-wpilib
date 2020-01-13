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
        "The error is also printed to the program console.");