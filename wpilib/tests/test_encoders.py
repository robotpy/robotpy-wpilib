import pytest

@pytest.fixture(scope="function")
def encoder_data(hal_data):
    return hal_data["encoder"][0]


#The simulated hal data for an encoder appears to be structured like this:
#["initialized"] (bool)
#["config"] (list)
#["reverse_direction"] (bool)

#The config for an encoder appears to be a list ordered as follows:
#port_a_module 0
#port_a_pin
#port_a_analog_trigger False
#port_b_module 0
#port_b_pin
#port_b_analog_trigger False

def test_channel_channel_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == False
    x.free()
    assert encoder_data["initialized"] == False


def test_channel_channel_reverse_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, True)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == True
    x.free()
    assert encoder_data["initialized"] == False


def test_channel_channel_reverse_type_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, True, wpilib.Encoder.EncodingType.k4X)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == True
    x.free()
    assert encoder_data["initialized"] == False


def test_channel_channel_channel_reverse_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, 3, True)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == True
    x.free()
    assert encoder_data["initialized"] == False


def test_channel_channel_channel_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, 3)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == False
    x.free()
    assert encoder_data["initialized"] == False


def test_source_source_reverse_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    x = wpilib.Encoder(s1, s2, True)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == True
    x.free()
    s1.free()
    s2.free()
    assert encoder_data["initialized"] == False


def test_source_source_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    x = wpilib.Encoder(s1, s2)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == False
    x.free()
    s1.free()
    s2.free()
    assert encoder_data["initialized"] == False


def test_source_source_reverse_type_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    x = wpilib.Encoder(s1, s2, True, wpilib.Encoder.EncodingType.k4X)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == True
    x.free()
    s1.free()
    s2.free()
    assert encoder_data["initialized"] == False


def test_source_source_source_reverse_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    s3 = wpilib.DigitalInput(3)
    x = wpilib.Encoder(s1, s2, s3, True)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == True
    x.free()
    s1.free()
    s2.free()
    s3.free()
    assert encoder_data["initialized"] == False


def test_source_source_source_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    s3 = wpilib.DigitalInput(3)
    x = wpilib.Encoder(s1, s2, s3)
    assert encoder_data["initialized"] == True
    assert encoder_data['config'] == [0, 1, False, 0, 2, False]
    assert encoder_data['reverse_direction'] == False
    x.free()
    s1.free()
    s2.free()
    s3.free()
    assert encoder_data["initialized"] == False