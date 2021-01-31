import warnings

warnings.warn(
    "wpilib.kinematics has moved to wpimath.kinematics", FutureWarning, stacklevel=2
)

from wpimath.kinematics import (
    ChassisSpeeds,
    DifferentialDriveKinematics,
    DifferentialDriveOdometry,
    DifferentialDriveWheelSpeeds,
    MecanumDriveKinematics,
    MecanumDriveOdometry,
    MecanumDriveWheelSpeeds,
    SwerveDrive3Kinematics,
    SwerveDrive3Odometry,
    SwerveDrive4Kinematics,
    SwerveDrive4Odometry,
    SwerveDrive6Kinematics,
    SwerveDrive6Odometry,
    SwerveModuleState,
)

__all__ = [
    "ChassisSpeeds",
    "DifferentialDriveKinematics",
    "DifferentialDriveOdometry",
    "DifferentialDriveWheelSpeeds",
    "MecanumDriveKinematics",
    "MecanumDriveOdometry",
    "MecanumDriveWheelSpeeds",
    "SwerveDrive3Kinematics",
    "SwerveDrive3Odometry",
    "SwerveDrive4Kinematics",
    "SwerveDrive4Odometry",
    "SwerveDrive6Kinematics",
    "SwerveDrive6Odometry",
    "SwerveModuleState",
]
