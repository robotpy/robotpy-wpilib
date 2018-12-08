import pytest


def test_glitch_filters(wpilib, hal_data):

    inputs = []
    filters = []

    for i in range(3):
        d = wpilib.DigitalInput(i)
        f = wpilib.DigitalGlitchFilter()
        f.add(d)
        filters.append((i, d, f))

        assert hal_data["dio"][i]["filterIndex"] == i

    # shouldn't be able to allocate another
    with pytest.raises(ValueError):
        f = wpilib.DigitalGlitchFilter()

    # free them
    for i, d, f in filters:
        f.remove(d)
        f.close()

        assert hal_data["dio"][i]["filterIndex"] is None
