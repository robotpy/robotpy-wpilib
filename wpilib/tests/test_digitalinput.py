import pytest
import hal


@pytest.fixture(scope='function')
def digitalinput(wpilib):
    return wpilib.DigitalInput(2)


@pytest.fixture(scope='function')
def di_data(hal_data):
    return hal_data['dio'][2]


@pytest.fixture(scope='function')
def di_data(hal_data):
    return hal_data['dio'][2]


@pytest.fixture(scope='function')
def di_table(networktables):
    return networktables.NetworkTables.getTable("/LiveWindow/DigitalInput/2")


def test_digitalinput_init(wpilib, di_data):
    di = wpilib.DigitalInput(2)
    assert di_data['initialized']
    assert di_data['is_input']


def test_digitalinput_free(digitalinput, wpilib):
    with pytest.raises(hal.exceptions.HALError):
        di2 = wpilib.DigitalInput(2)

    digitalinput.free()

    di2 = wpilib.DigitalInput(2)


def test_digitalinput_get(digitalinput, di_data):
    di_data['value'] = True
    assert digitalinput.get()


def test_digitalinput_getChannel(digitalinput):
    assert digitalinput.getChannel() == 2


def test_digitalinput_getAnalogTriggerTypeForRouting(digitalinput):
    assert digitalinput.getAnalogTriggerTypeForRouting() == 0


def test_digitalinput_isAnalogTrigger(digitalinput):
    assert not digitalinput.isAnalogTrigger()


def test_digitalinput_initTable_null(digitalinput):
    digitalinput.initTable(None)
    assert digitalinput.valueEntry is None


def test_digitalinput_initTable(digitalinput, di_table, di_data):
    di_data['value'] = True

    digitalinput.initTable(di_table)

    assert di_table.getBoolean('Value', False) == True
