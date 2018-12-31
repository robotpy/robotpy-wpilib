# validated: 2018-11-17 EN 8373e0361b2c edu/wpi/first/wpilibj/Controller.java
__all__ = ["Controller"]


class Controller:
    """An interface for controllers. Controllers run control loops, the most
    command are PID controllers and there variants, but this includes anything
    that is controlling an actuator in a separate thread.
    """

    def enable(self) -> None:
        """Allows the control loop to run."""
        raise NotImplementedError

    def disable(self) -> None:
        """Stops the control loop from running until explicitly re-enabled by
        calling :meth:`enable`.
        """
        raise NotImplementedError
