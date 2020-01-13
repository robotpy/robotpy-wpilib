
auto logger = py::module::import("logging").attr("getLogger")("robot");
cls_RobotBase.attr("logger") = logger;

cls_RobotBase.def_static(
    "main",
    [](py::object robot_cls) -> py::object {
      auto start = py::module::import("wpilib._impl.start");
      auto starter = start.attr("RobotStarter")();
      return starter.attr("run")(robot_cls);
    },
    py::arg("robot_cls"), "Starting point for the application");