# validated: 2017-10-23 TW 9dc1de1d09da edu/wpi/first/wpilibj/drive/Vector2d.java
import math

__all__ = ["Vector2d"]


class Vector2d:
    """This is a 2D vector struct that supports basic operations"""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """Construct a 2D vector

        :param x: x component of the vector
        :param y: y component of the vector
        """
        self.x = x
        self.y = y

    def rotate(self, angle: float) -> None:
        """Rotate a vector in Cartesian space.

        :param angle: Angle in degrees by which to rotate vector counter-clockwise
        """
        angle = math.radians(angle)
        cosA = math.cos(angle)
        sinA = math.sin(angle)

        x = self.x * cosA - self.y * sinA
        y = self.x * sinA + self.y * cosA
        self.x = x
        self.y = y

    def dot(self, vec: "Vector2d") -> float:
        """Returns dot product of this vector and argument

        :param vec: Vector with which to perform dot product
        """
        return self.x * vec.x + self.y * vec.y

    def magnitude(self) -> float:
        """ Returns magnitude of vector"""
        return math.hypot(self.x, self.y)

    def scalarProject(self, vec: "Vector2d") -> float:
        """Returns scalar projection of this vector onto argument

        :param vec: Vector onto which to project this vector
        :return: scalar projection of this vector onto argument
        """
        return self.dot(vec) / vec.magnitude()
