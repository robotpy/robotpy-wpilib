"""
    Various helper functions useful for interacting with the HAL data
"""

from . import data

hal_data = data.hal_data
from . import functions as fns


def notify_new_ds_data():
    """Called when driver station data is modified"""
    data.hooks.notifyDSData()


def set_autonomous(enabled, game_specific_message=None):
    """Only designed to be called on transition"""

    if game_specific_message:
        hal_data["event"]["game_specific_message"] = game_specific_message

    hal_data["control"].update(
        {"autonomous": True, "test": False, "enabled": enabled, "dsAttached": True}
    )

    if enabled:
        hal_data["time"]["remaining"] = 135000000
    else:
        hal_data["time"]["remaining"] = None

    notify_new_ds_data()


def set_test_mode(enabled):
    """Only designed to be called on transition"""

    hal_data["control"].update(
        {"autonomous": False, "test": True, "enabled": enabled, "dsAttached": True}
    )

    hal_data["time"]["remaining"] = None
    notify_new_ds_data()


def set_teleop_mode(enabled):
    """Only designed to be called on transition"""

    hal_data["control"].update(
        {"autonomous": False, "test": False, "enabled": enabled, "dsAttached": True}
    )

    if enabled:
        hal_data["time"]["remaining"] = fns.hooks.getFPGATime() + 120000000
    else:
        hal_data["time"]["remaining"] = None

    notify_new_ds_data()


def set_disabled():
    """Only designed to be called on transition"""

    hal_data["control"].update(
        {"autonomous": False, "test": False, "enabled": False, "dsAttached": True}
    )

    hal_data["time"]["remaining"] = None

    notify_new_ds_data()


def set_estop():
    """Only designed to be called on transition"""

    hal_data["control"].update(
        {
            "autonomous": False,
            "test": False,
            "enabled": False,
            "dsAttached": True,
            "eStop": True,
        }
    )

    hal_data["time"]["remaining"] = None

    notify_new_ds_data()


def set_mode(new_mode, new_enabled, **kwargs):
    """
        Calls the appropriate function based on the mode string

        Can be called repeatedly, will only update a mode when it
        changes.

        :param new_mode: auto, test, or teleop
        :param enabled:  True if enabled, False otherwise
    """

    assert new_mode in ["auto", "test", "teleop"]
    new_enabled = bool(new_enabled)

    ctrl = hal_data["control"]

    enabled = ctrl["enabled"]
    if ctrl["autonomous"]:
        old_mode = "auto"
    elif ctrl["test"]:
        old_mode = "test"
    else:
        old_mode = "teleop"

    if new_mode != old_mode or enabled != new_enabled:
        if new_mode == "test":
            set_test_mode(new_enabled, **kwargs)
        elif new_mode == "auto":
            set_autonomous(new_enabled, **kwargs)
        elif new_mode == "teleop":
            set_teleop_mode(new_enabled, **kwargs)
