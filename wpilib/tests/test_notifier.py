
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
    
    n.free()

# TODO: better tests
