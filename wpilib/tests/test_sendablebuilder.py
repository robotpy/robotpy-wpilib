import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def builder(wpilib):
    return wpilib.SendableBuilder()


@pytest.fixture(scope="function")
def builder_table(networktables):
    return networktables.NetworkTables.getTable("sensor")


def test_sendablebuilder_addBooleanProperty1(builder, builder_table):
    builder.setTable(builder_table)
    builder.addBooleanProperty("Enabled", None, None)

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addBooleanProperty2(builder, builder_table):
    builder.setTable(builder_table)
    builder.addBooleanProperty("Enabled", lambda: True, None)
    assert builder.properties[0].key == "Enabled"

    builder.updateTable()
    assert builder_table.getBoolean("Enabled", False) == True
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addBooleanProperty3(builder, builder_table):
    enabledChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addBooleanProperty("Enabled", None, enabledChanged)
    assert builder.properties[0].key == "Enabled"

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addBooleanProperty4(builder, builder_table):
    enabledChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addBooleanProperty("Enabled", lambda: True, enabledChanged)
    assert builder.properties[0].key == "Enabled"

    builder.updateTable()
    assert builder_table.getBoolean("Enabled", False) == True
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleProperty1(builder, builder_table):
    builder.setTable(builder_table)
    builder.addDoubleProperty("p", None, None)

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleProperty2(builder, builder_table):
    builder.setTable(builder_table)
    builder.addDoubleProperty("p", lambda: 3.4, None)
    assert builder.properties[0].key == "p"

    builder.updateTable()
    assert builder_table.getNumber("p", 0.0) == 3.4
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleProperty3(builder, builder_table):
    pChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addDoubleProperty("p", None, pChanged)
    assert builder.properties[0].key == "p"

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleProperty4(builder, builder_table):
    pChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addDoubleProperty("p", lambda: 3.4, pChanged)
    assert builder.properties[0].key == "p"

    builder.updateTable()
    assert builder_table.getNumber("p", 0.0) == 3.4
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringProperty1(builder, builder_table):
    builder.setTable(builder_table)
    builder.addStringProperty("name", None, None)

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringProperty2(builder, builder_table):
    builder.setTable(builder_table)
    builder.addStringProperty("name", lambda: "percival", None)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getString("name", "") == "percival"
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringProperty3(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addStringProperty("name", None, nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringProperty4(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addStringProperty("name", lambda: "percival", nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getString("name", "") == "percival"
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addBooleanArrayProperty1(builder, builder_table):
    builder.setTable(builder_table)
    builder.addBooleanArrayProperty("name", None, None)

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addBooleanArrayProperty2(builder, builder_table):
    builder.setTable(builder_table)
    builder.addBooleanArrayProperty("name", lambda: [True, True, False], None)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getBooleanArray("name", []) == (True, True, False)
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addBooleanArrayProperty3(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addBooleanArrayProperty("name", None, nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addBooleanArrayProperty4(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addBooleanArrayProperty("name", lambda: [True, True, False], nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getBooleanArray("name", []) == (True, True, False)
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleArrayProperty1(builder, builder_table):
    builder.setTable(builder_table)
    builder.addDoubleArrayProperty("name", None, None)

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleArrayProperty2(builder, builder_table):
    builder.setTable(builder_table)
    builder.addDoubleArrayProperty("name", lambda: [3.14, 6.28, 11.0], None)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getNumberArray("name", []) == (3.14, 6.28, 11.0)
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleArrayProperty3(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addDoubleArrayProperty("name", None, nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addDoubleArrayProperty4(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addDoubleArrayProperty("name", lambda: [3.14, 6.28, 11.0], nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getNumberArray("name", []) == (3.14, 6.28, 11.0)
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringArrayProperty1(builder, builder_table):
    builder.setTable(builder_table)
    builder.addStringArrayProperty("name", None, None)

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringArrayProperty2(builder, builder_table):
    builder.setTable(builder_table)
    builder.addStringArrayProperty("name", lambda: ["fi", "fie", "fo"], None)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getStringArray("name", []) == ("fi", "fie", "fo")
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringArrayProperty3(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addStringArrayProperty("name", None, nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_addStringArrayProperty4(builder, builder_table):
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.addStringArrayProperty("name", lambda: ["fi", "fie", "fo"], nameChanged)
    assert builder.properties[0].key == "name"

    builder.updateTable()
    assert builder_table.getStringArray("name", []) == ("fi", "fie", "fo")
    builder.startLiveWindowMode()
    assert builder.properties[0].listener is not None
    builder.stopLiveWindowMode()
    assert builder.properties[0].listener is None


def test_sendablebuilder_safestate(builder, builder_table):
    safeState = MagicMock()
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.setSafeState(safeState)
    builder.addStringProperty("name", lambda: "percival", nameChanged)

    builder.updateTable()
    assert not safeState.called
    builder.startLiveWindowMode()
    assert safeState.called
    safeState.called = False
    builder.stopLiveWindowMode()
    assert safeState.called


def test_sendablebuilder_updatetable(builder, builder_table):
    updateTable = MagicMock()
    nameChanged = MagicMock()
    builder.setTable(builder_table)
    builder.setUpdateTable(updateTable)
    builder.addStringProperty("name", lambda: "percival", nameChanged)

    assert not updateTable.called
    builder.updateTable()
    assert updateTable.called
    updateTable.called = False
    builder.startLiveWindowMode()
    assert not updateTable.called
    builder.stopLiveWindowMode()
    assert not updateTable.called
