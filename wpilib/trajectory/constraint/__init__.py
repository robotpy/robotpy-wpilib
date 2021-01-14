import warnings

warnings.warn(
    "wpilib.trajectory.constraint has moved to wpimath.trajectory.constraint",
    FutureWarning,
)


from wpimath.trajectory.constraint import (
    CentripetalAccelerationConstraint,
    DifferentialDriveKinematicsConstraint,
    DifferentialDriveVoltageConstraint,
    MecanumDriveKinematicsConstraint,
    SwerveDrive3KinematicsConstraint,
    SwerveDrive4KinematicsConstraint,
    SwerveDrive6KinematicsConstraint,
    TrajectoryConstraint,
)

__all__ = [
    "CentripetalAccelerationConstraint",
    "DifferentialDriveKinematicsConstraint",
    "DifferentialDriveVoltageConstraint",
    "MecanumDriveKinematicsConstraint",
    "SwerveDrive3KinematicsConstraint",
    "SwerveDrive4KinematicsConstraint",
    "SwerveDrive6KinematicsConstraint",
    "TrajectoryConstraint",
]
