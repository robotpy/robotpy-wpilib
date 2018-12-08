import pytest


@pytest.fixture(scope="function")
def getTable(networktables):
    return networktables.NetworkTables.getTable


def test_enableActuatorWidgets(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add("simplevalue", 1)
    d_output = wpilib.DigitalOutput(1)
    motor = wpilib.NidecBrushless(2, 3)
    layout = tab.getLayout("tortilla", "the_tortilla")
    layout.add("complexvalue", d_output)
    layout.add(motor)
    wpilib.shuffleboard.Shuffleboard.update()
    wpilib.shuffleboard.Shuffleboard.enableActuatorWidgets()
    wpilib.shuffleboard.Shuffleboard.disableActuatorWidgets()


def test_addPersistent(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    widget = tab.addPersistent("simplevalue", 1)
    # k, how to kick networktables?
    # assert widget.getEntry().isPersistent()


def test_getTab(wpilib, getTable):
    shuffleTable = getTable("/Shuffleboard")
    metaTable = getTable("/Shuffleboard/.metadata")

    assert metaTable.getStringArray("Tabs", []) == []
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add("simplevalue", 1)
    assert metaTable.getStringArray("Tabs", []) == ("tacos",)


def test_setType(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add("street_taco", 1).setType("taco")
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getString("PreferredComponent", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getString("PreferredComponent", None) == "taco"


def test_withProperties(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add("street_taco", 1).withProperties({"sauce": "spicy"})
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco/Properties")
    assert tacoTable.getString("sauce", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getString("sauce", None) == "spicy"


def test_withPosition(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add("street_taco", 1).withPosition(columnIndex=4, rowIndex=5)
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getNumberArray("Position", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getNumberArray("Position", None) == (4.0, 5.0)


def test_withSize(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add("street_taco", 1).withSize(width=300, height=200)
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getNumberArray("Size", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getNumberArray("Size", None) == (300.0, 200.0)


def test_withWidget(wpilib, getTable):
    tab = wpilib.shuffleboard.Shuffleboard.getTab("tacos")
    tab.add("street_taco", 1).withWidget("guacamole")
    tacoTable = getTable("/Shuffleboard/.metadata/tacos/street_taco")
    assert tacoTable.getString("PreferredComponent", None) is None
    wpilib.shuffleboard.Shuffleboard.update()
    assert tacoTable.getString("PreferredComponent", None) == "guacamole"
