
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
        [](RobotBase *that) -> std::tuple<bool, bool, bool> {
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
