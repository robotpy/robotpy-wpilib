real = True
oi = None
subsystems = dict()


def is_simulated():
    """:return True if the robot is simulated."""
    return not real


def is_real():
    """:return True if the robot is real"""
    return real