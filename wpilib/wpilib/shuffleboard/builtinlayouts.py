# validated: 2019-01-10 DV 01d13220660c edu/wpi/first/wpilibj/shuffleboard/BuiltInLayouts.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import enum


class BuiltInLayouts(enum.Enum):
    """The types of layouts bundled with Shuffleboard.

    ::

        myList = (
            Shuffleboard.getTab("My Tab")
            .getLayout(BuiltinLayouts.kList, "My List")
        )
    """

    #: Groups components in a vertical list.
    #: New widgets added to the layout will be placed at the bottom of the list.
    #:
    #: Custom properties:
    #:
    #: ============== ====== ============= ========================================================================================================
    #: Name           Type   Default Value Notes
    #: ============== ====== ============= ========================================================================================================
    #: Label position String "BOTTOM"      The position of component labels inside the grid. One of ``["TOP", "LEFT", "BOTTOM", "RIGHT", "HIDDEN"``
    #: ============== ====== ============= ========================================================================================================
    kList = "List Layout"

    #: Groups components in an `n` x `m` grid. Grid layouts default to 3x3.
    #:
    #: Custom properties:
    #:
    #: ================= ====== ============= ========================================================================================================
    #: Name              Type   Default Value Notes
    #: ================= ====== ============= ========================================================================================================
    #: Number of columns Number 3             Must be in the range [1,15]
    #: Number of rows    Number 3             Must be in the range [1,15]
    #: Label position    String "BOTTOM"      The position of component labels inside the grid. One of ``["TOP", "LEFT", "BOTTOM", "RIGHT", "HIDDEN"``
    #: ================= ====== ============= ========================================================================================================
    kGrid = "Grid Layout"
