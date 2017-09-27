# validated: 2017-09-27 AA e1195e8b9dab edu/wpi/first/wpilibj/Controller.java
__all__ = ["Controller"]

class Controller:
    """An interface for controllers. Controllers run control loops, the most
    command are PID controllers and there variants, but this includes anything
    that is controlling an actuator in a separate thread.
    """
    def enable(self):
        """Allows the control loop to run."""
        raise NotImplementedError

    def disable(self):
        """Stops the control loop from running until explicitly re-enabled by
        calling :meth:`enable`.
        """
        raise NotImplementedError
