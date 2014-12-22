from unittest.mock import Mock
import pytest

def test_match_arglist(wpilib):

    argument_templates = [[("arg1", bool)],
                          [("arg1", bool), ("arg2", str)],
                          [("arg1", str), ("arg3", wpilib._impl.utils.HasAttribute("foo"))]]
    bar = Mock()
    bar.foo = "hola!"

    index, result = wpilib._impl.utils.match_arglist("", [True, ], {}, argument_templates)
    assert index == 0
    assert result["arg1"] is True

    index, result = wpilib._impl.utils.match_arglist("", [False, "hi"], {}, argument_templates)
    assert index == 1
    assert result["arg1"] is False
    assert result["arg2"] == "hi"

    index, result = wpilib._impl.utils.match_arglist("", ["haha", bar], {}, argument_templates)
    assert index == 2
    assert result["arg1"] == "haha"
    assert result["arg3"].foo == "hola!"

    index, result = wpilib._impl.utils.match_arglist("", [], {"arg1": False, "arg2": "hi"}, argument_templates)
    assert index == 1
    assert result["arg1"] is False
    assert result["arg2"] == "hi"

    with pytest.raises(ValueError):
        _, _ = wpilib._impl.utils.match_arglist("", [5], {}, argument_templates)

    with pytest.raises(ValueError):
        _, _ = wpilib._impl.utils.match_arglist("", [True, bar], {}, argument_templates)

    with pytest.raises(ValueError):
        _, _ = wpilib._impl.utils.match_arglist("", [True, bar, False], {}, argument_templates)


