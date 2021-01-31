import warnings

warnings.warn("wpilib.spline has moved to wpimath.spline", FutureWarning, stacklevel=2)

from wpimath.spline import (
    CubicHermiteSpline,
    QuinticHermiteSpline,
    Spline3,
    Spline5,
    SplineHelper,
    SplineParameterizer,
)

__all__ = [
    "CubicHermiteSpline",
    "QuinticHermiteSpline",
    "Spline3",
    "Spline5",
    "SplineHelper",
    "SplineParameterizer",
]
