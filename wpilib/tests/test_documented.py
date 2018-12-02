import inspect


def test_all_classes_documented(wpilib):
    expected_undocumented = {
        wpilib: {"Notifier", "SendableBuilder"},
        wpilib.buttons: set(),
        wpilib.command: set(),
        wpilib.drive: set(),
        wpilib.interfaces: set(),
    }

    for package, expected_class_names in expected_undocumented.items():
        actual_undocumented = set()
        for name, cls in inspect.getmembers(package, inspect.isclass):
            if not cls.__doc__:
                actual_undocumented.add(name)
        assert actual_undocumented == expected_class_names
