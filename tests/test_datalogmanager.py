import tempfile
import pytest
import wpilib


def test_get_log():
    with tempfile.TemporaryDirectory() as tmpdir:
        wpilib.DataLogManager.start(tmpdir)
        log = wpilib.DataLogManager.getLog()
        assert log is not None
