"""Step 7: ``to_dict`` / ``from_dict`` round-trip for the ladder-floor value types
(``Groupable``, ``Unified``) -- Gemini's "one thing": a complete value object must
serialize and deserialize without information loss.
"""
from dazzle_lib import Groupable, Unified


def test_groupable_round_trips():
    g = Groupable.unified("on", meaning="power")
    assert Groupable.from_dict(g.to_dict()) == g
    assert g.to_dict() == {"minus": "not-on", "plus": "on", "meaning": "power"}


def test_unified_round_trips():
    u = Unified("print", meaning="output")
    assert Unified.from_dict(u.to_dict()) == u
    assert u.to_dict() == {"label": "print", "meaning": "output"}


def test_groupable_from_dict_tolerates_missing_meaning():
    g = Groupable.from_dict({"minus": "a", "plus": "b"})
    assert g == Groupable(minus="a", plus="b", meaning="")


def test_schema_version_present():
    assert Groupable.SCHEMA_VERSION == 1
    assert Unified.SCHEMA_VERSION == 1
