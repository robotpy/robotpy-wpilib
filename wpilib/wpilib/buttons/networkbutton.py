# validated: 2017-10-19 AA 4e80570c4c48 edu/wpi/first/wpilibj/buttons/NetworkButton.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .button import Button

from networktables.networktable import NetworkTable
from networktables import NetworkTablesInstance

__all__ = ["NetworkButton"]


class NetworkButton(Button):
    """A :class:`.button.Button` that uses a :class:`.NetworkTable` boolean field."""

    def __init__(self, table: NetworkTable, field: str) -> None:
        """Initialize the NetworkButton.

        :param table: the :class:`.NetworkTable` instance to use, or the name of the
                      table to use.
        :param field: field to use.
        """
        if isinstance(table, NetworkTable):
            self.entry = table.getEntry(field)
        else:
            table = NetworkTablesInstance.getDefault().getTable(table)
            self.entry = table.getEntry(field)

    def get(self) -> bool:
        """Get the value of the button."""
        return self.entry.getInstance().isConnected() and self.entry.getBoolean(False)
