import warnings

warnings.warn(
    "wpilib.trajectory has moved to wpimath.trajectory", FutureWarning, stacklevel=2
)

from wpimath.trajectory import (
    Trajectory,
    TrajectoryConfig,
    TrajectoryGenerator,
    TrajectoryParameterizer,
    TrajectoryUtil,
    TrapezoidProfile,
)

__all__ = [
    "Trajectory",
    "TrajectoryConfig",
    "TrajectoryGenerator",
    "TrajectoryParameterizer",
    "TrajectoryUtil",
    "TrapezoidProfile",
]
