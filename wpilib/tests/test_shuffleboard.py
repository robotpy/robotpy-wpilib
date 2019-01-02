import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(scope="function")
def getTable(networktables):
    return networktables.NetworkTables.getTable


@pytest.fixture(scope="function")
def recordingcontroller(wpilib, networktables):
    nt_instance = networktables.NetworkTables
    rc = wpilib.shuffleboard.recordingcontroller.RecordingController(nt_instance)
    return rc


def test_enableActuatorWidgets(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add(title="simplevalue", value=1)
    d_output = wpilib.DigitalOutput(1)
    motor = wpilib.NidecBrushless(2, 3)
    layout = tab.getLayout("tortilla", "the_tortilla")
    layout.add(title="complexvalue", value=d_output)
    layout.add(motor)
    wpilib.shuffleboard.Shuffleboard.update()
    wpilib.shuffleboard.Shuffleboard.enableActuatorWidgets()
    wpilib.shuffleboard.Shuffleboard.disableActuatorWidgets()


def test_addPersistent(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    widget = tab.addPersistent("simplevalue", 1)
    assert widget.getEntry().isPersistent()


def test_getTab(wpilib, getTable):
    metaTable = getTable("/Shuffleboard/.metadata")

    assert metaTable.getStringArray("Tabs", []) == []
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add(1, title="simplevalue")
    assert metaTable.getStringArray("Tabs", []) == ("tacos",)


def test_setType(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add(title="street_taco", value=1).setType("taco")
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getString("PreferredComponent", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getString("PreferredComponent", None) == "taco"


def test_withProperties(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add(title="street_taco", value=1).withProperties({"sauce": "spicy"})
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco/Properties")
    assert tacoTable.getString("sauce", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getString("sauce", None) == "spicy"


def test_withPosition(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add(title="street_taco", value=1).withPosition(columnIndex=4, rowIndex=5)
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getNumberArray("Position", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getNumberArray("Position", None) == (4.0, 5.0)


def test_withSize(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add(title="street_taco", value=1).withSize(width=300, height=200)
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getNumberArray("Size", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getNumberArray("Size", None) == (300.0, 200.0)


def test_withWidget(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add(title="street_taco", value=1).withWidget("guacamole")
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getString("PreferredComponent", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getString("PreferredComponent", None) == "guacamole"


def test_selectTab_byIndex(wpilib):
    wpilib.shuffleboard.Shuffleboard.selectTab(1)


def test_recording(wpilib):
    wpilib.shuffleboard.Shuffleboard.startRecording()
    wpilib.shuffleboard.Shuffleboard.stopRecording()


def test_RecordingController_init(wpilib, networktables):
    nt_instance = networktables.instance.NetworkTablesInstance.getDefault()
    rc = wpilib.shuffleboard.recordingcontroller.RecordingController(nt_instance)
    assert rc.eventsTable.path == "/Shuffleboard/.recording/events"
    assert (
        rc.recordingFileNameFormatEntry.getName()
        == "/Shuffleboard/.recording/FileNameFormat"
    )
    assert rc.recordingControlEntry.getName() == "/Shuffleboard/.recording/RecordData"


def test_RecordingController_startRecording(recordingcontroller):
    rc = recordingcontroller
    assert rc.recordingControlEntry.getBoolean(None) is None
    rc.startRecording()
    assert rc.recordingControlEntry.getBoolean(None)
    rc.stopRecording()
    assert rc.recordingControlEntry.getBoolean(None) is False
    rc.startRecording()
    assert rc.recordingControlEntry.getBoolean(None)


def test_RecordingController_setRecordingFileNameFormat(recordingcontroller):
    rc = recordingcontroller
    assert rc.recordingFileNameFormatEntry.getString(None) is None
    rc.setRecordingFileNameFormat("tacos")
    assert rc.recordingFileNameFormatEntry.getString(None) == "tacos"
    rc.clearRecordingFileNameFormat()
    assert rc.recordingFileNameFormatEntry.getString(None) is None


@pytest.fixture(scope="function")
def DriverStation(wpilib):
    with patch(
        "wpilib.shuffleboard.recordingcontroller.DriverStation", new=MagicMock()
    ) as ds:
        yield ds


@pytest.mark.parametrize(
    "name, description, importance_name, expected",
    [
        (
            "percival",
            "red ring of marshmallows",
            "kTrivial",
            ("red ring of marshmallows", "TRIVIAL"),
        ),
        ("percival", "\t", "kTrivial", ("", "TRIVIAL")),
        ("percival", None, "kTrivial", ("", "TRIVIAL")),
    ],
)
def test_RecordingController_addEventMarker(
    wpilib, recordingcontroller, name, description, importance_name, expected
):
    rc = recordingcontroller
    importance = getattr(wpilib.shuffleboard.EventImportance, importance_name)
    rc.addEventMarker(name, description, importance)
    assert rc.eventsTable.getSubTable(name).getStringArray("Info", None) == expected


@pytest.mark.parametrize("name", [(""), ("  "), ("\t"), ("\n")])
def test_RecordingController_addEventMarker_refuses_name(
    wpilib, recordingcontroller, DriverStation, name
):
    rc = recordingcontroller
    rc.addEventMarker(name, "tacos", wpilib.shuffleboard.EventImportance.kCritical)
    DriverStation.reportError.assert_called_with(
        "Shuffleboard event name was not specified", True
    )


def test_Shuffleboard_addEventMarker1(wpilib, networktables):
    importance = wpilib.shuffleboard.EventImportance.kTrivial
    wpilib.shuffleboard.Shuffleboard.addEventMarker(
        "percival", importance, "red ring of marshmallows"
    )

    table = networktables.NetworkTables.getTable(
        "/Shuffleboard/.recording/events/percival"
    )
    assert table.getStringArray("Info", None) == ("red ring of marshmallows", "TRIVIAL")


def test_Shuffleboard_addEventMarker2(wpilib, networktables):
    importance = wpilib.shuffleboard.EventImportance.kTrivial
    wpilib.shuffleboard.Shuffleboard.addEventMarker("percival", importance)

    table = networktables.NetworkTables.getTable(
        "/Shuffleboard/.recording/events/percival"
    )
    assert table.getStringArray("Info", None) == ("", "TRIVIAL")


def test_Shuffleboard_setRecordingFileNameFormat(wpilib):
    rc = wpilib.shuffleboard.Shuffleboard._recordingController = MagicMock()
    wpilib.shuffleboard.Shuffleboard.setRecordingFileNameFormat("percival")
    rc.setRecordingFileNameFormat.assert_called_with("percival")
    wpilib.shuffleboard.Shuffleboard.clearRecordingFileNameFormat()
    rc.clearRecordingFileNameFormat.assert_called_with()
