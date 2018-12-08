from unittest.mock import Mock
import pytest


def test_match_arglist(wpilib):

    argument_templates = [
        [("arg1", bool)],
        [("arg1", bool), ("arg2", str)],
        [("arg1", str), ("arg3", wpilib._impl.utils.HasAttribute("foo"))],
    ]
    bar = Mock()
    bar.foo = "hola!"

    index, result = wpilib._impl.utils.match_arglist(
        "v1", [True], {}, argument_templates
    )
    assert index == 0
    assert result["arg1"] is True
    assert len(result) == 1

    index, result = wpilib._impl.utils.match_arglist(
        "v4", [], {"arg1": False}, argument_templates
    )
    assert index == 0
    assert result["arg1"] is False
    assert len(result) == 1

    index, result = wpilib._impl.utils.match_arglist(
        "v2", [False, "hi"], {}, argument_templates
    )
    assert index == 1
    assert result["arg1"] is False
    assert result["arg2"] == "hi"
    assert len(result) == 2

    index, result = wpilib._impl.utils.match_arglist(
        "v3", ["haha", bar], {}, argument_templates
    )
    assert index == 2
    assert result["arg1"] == "haha"
    assert result["arg3"].foo == "hola!"
    assert len(result) == 2

    index, result = wpilib._impl.utils.match_arglist(
        "v4", [], {"arg1": False, "arg2": "hi"}, argument_templates
    )
    assert index == 1
    assert result["arg1"] is False
    assert result["arg2"] == "hi"
    assert len(result) == 2

    index, result = wpilib._impl.utils.match_arglist(
        "v5", [False], {"arg2": "hi"}, argument_templates
    )
    assert index == 1
    assert result["arg1"] is False
    assert result["arg2"] == "hi"
    assert len(result) == 2

    with pytest.raises(ValueError):
        _, _ = wpilib._impl.utils.match_arglist("v6", [5], {}, argument_templates)

    with pytest.raises(ValueError):
        _, _ = wpilib._impl.utils.match_arglist(
            "v7", [True, bar], {}, argument_templates
        )

    with pytest.raises(ValueError):
        _, _ = wpilib._impl.utils.match_arglist(
            "v8", [True, bar, False], {}, argument_templates
        )

    with pytest.raises(ValueError):
        # kw argument before positional argument ("hi", arg1=True)
        _, _ = wpilib._impl.utils.match_arglist(
            "v9", ["hi"], {"arg1": True}, argument_templates
        )

    with pytest.raises(ValueError):
        # extra kw argument
        _, _ = wpilib._impl.utils.match_arglist(
            "v10", [True], {"something": True}, argument_templates
        )
