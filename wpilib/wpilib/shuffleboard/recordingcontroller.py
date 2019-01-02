# validated: 2018-12-15 EN 45f4472d4224 edu/wpi/first/wpilibj/shuffleboard/RecordingController.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from ..driverstation import DriverStation
from networktables.instance import NetworkTablesInstance
from .eventimportance import EventImportance


__all__ = ["RecordingController"]


class RecordingController:
    """Controls Shuffleboard recordings via NetworkTables."""

    kRecordingTableName = "/Shuffleboard/.recording/"
    kRecordingControlKey = kRecordingTableName + "RecordData"
    kRecordingFileNameFormatKey = kRecordingTableName + "FileNameFormat"
    kEventMarkerTableName = kRecordingTableName + "events"

    def __init__(self, ntInstance: NetworkTablesInstance) -> None:
        self.recordingControlEntry = ntInstance.getEntry(
            RecordingController.kRecordingControlKey
        )
        self.recordingFileNameFormatEntry = ntInstance.getEntry(
            RecordingController.kRecordingFileNameFormatKey
        )
        self.eventsTable = ntInstance.getTable(
            RecordingController.kEventMarkerTableName
        )

    def startRecording(self) -> None:
        self.recordingControlEntry.setBoolean(True)

    def stopRecording(self) -> None:
        self.recordingControlEntry.setBoolean(False)

    def setRecordingFileNameFormat(self, format: str) -> None:
        self.recordingFileNameFormatEntry.setString(format)

    def clearRecordingFileNameFormat(self) -> None:
        self.recordingFileNameFormatEntry.delete()

    def addEventMarker(self, name: str, description: str, importance: EventImportance):
        if not name or name.isspace():
            DriverStation.reportError("Shuffleboard event name was not specified", True)
            return

        eventDescription = description

        if description is None or description.isspace():
            eventDescription = ""

        self.eventsTable.getSubTable(name).getEntry("Info").setStringArray(
            [eventDescription, importance.value]
        )
