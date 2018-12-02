import threading


def test_notifier_single(wpilib):

    c = threading.Condition()

    def _fn():
        with c:
            c.notify_all()

    n = wpilib.Notifier(run=_fn)
    with c:
        n.startSingle(0.05)
        assert c.wait(timeout=1.0)

    n.close()


def test_notifier_periodic(wpilib):

    c = threading.Condition()

    def _fn():
        with c:
            c.notify_all()

    n = wpilib.Notifier(run=_fn)
    with c:
        n.startPeriodic(0.05)
        assert c.wait(timeout=1.0)
        assert c.wait(timeout=1.0)
        n.stop()
    n.close()


# TODO: better tests
