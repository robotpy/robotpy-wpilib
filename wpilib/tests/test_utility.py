import pytest


@pytest.fixture(scope="function")
def util(wpilib):
    return wpilib.Utility


def test_utility_getFPGAVersion(util):
    assert util.getFPGAVersion() == 2018


def test_utility_getFPGARevision(util):
    assert util.getFPGARevision() == 0


def test_utility_getFPGATime(util, hal_data, monkeypatch):
    import time

    monkeypatch.setattr(time, "monotonic", lambda: 3.14)
    hal_data["time"]["program_start"] = 1
    assert util.getFPGATime() == 2.14 * 1000000


def test_utility_getUserButton(util, hal_data):
    hal_data["fpga_button"] = True
    assert util.getUserButton() == True
