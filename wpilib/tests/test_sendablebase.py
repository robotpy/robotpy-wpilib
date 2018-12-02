import pytest


@pytest.fixture(scope="function")
def sendablebase(wpilib):
    return wpilib.SendableBase(False)


def test_sendablebase_init(wpilib):
    sb = wpilib.SendableBase(False)


def test_sendablebase_setname1(sendablebase):
    sendablebase.setName("Ultrasonic")

    assert sendablebase.getName() == "Ultrasonic"


def test_sendablebase_setname2(sendablebase):
    sendablebase.setName("Group1", "Ultrasonic")

    assert sendablebase.getName() == "Ultrasonic"
    assert sendablebase.getSubsystem() == "Group1"


def test_sendablebase_setname2(sendablebase):
    sendablebase.setName("Ultrasonic", 1)

    assert sendablebase.getName() == "Ultrasonic[1]"


def test_sendablebase_setname3(sendablebase):
    sendablebase.setName("Ultrasonic", 1, 2)

    assert sendablebase.getName() == "Ultrasonic[1,2]"


def test_sendablebase_setname4(sendablebase):
    with pytest.raises(ValueError) as excinfo:
        sendablebase.setName("Ultrasonic", 1, 2, 3)
