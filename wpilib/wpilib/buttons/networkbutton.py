#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .button import Button

__all__ = ["NetworkButton"]

class NetworkButton(Button):
    def __init__(self, table, field):
        from networktables import NetworkTable
        if isinstance(table, NetworkTable):
            self.table = table
        else:
            self.table = NetworkTable.getTable(table)
        self.field = field

    def get(self):
        return self.table.isConnected() and self.table.getBoolean(self.field, False)
