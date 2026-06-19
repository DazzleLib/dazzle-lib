"""Tests for the Step-2 ladder bridges on ``Continuum``:
``poles()``, ``densify_between()``, ``from_groupable()``.

Ports spike C1 (poles -> Groupable) + C2 (exact mediant densification) from
dazzlecmd's latent-recursion spike. The production ``Continuum`` stays
NAME-keyed; densification adds Fraction-positioned named rungs without touching
existing int rungs (byte-transparent).
"""
from fractions import Fraction

import pytest

from dazzle_lib import Continuum, ContinuumError, Groupable


def _ladder() -> Continuum:
    return Continuum(
        name="presence",
        ranks={"hidden": -2, "shadow": -1, "neutral": 0, "active": 1},
        invariant="presence",
    )


def test_poles_returns_groupable_bounds():
    g = _ladder().poles()
    assert isinstance(g, Groupable)
    assert g.minus == "hidden" and g.plus == "active"  # cold pole / warm pole
    assert g.meaning == "presence"


def test_densify_between_inserts_mediant():
    d = _ladder().densify_between("neutral", "active", "half")  # between 0 and 1
    assert d.rank("half") == Fraction(1, 2)
    assert Fraction(0) < d.rank("half") < Fraction(1)
    # existing rungs untouched
    assert d.rank("neutral") == 0 and d.rank("active") == 1
    # ordering places the new rung correctly
    assert d.levels() == ("hidden", "shadow", "neutral", "half", "active")


def test_densify_is_exact_and_repeatable():
    c = Continuum(name="x", ranks={"lo": 0, "hi": 1}, invariant="x")
    lower = "lo"
    for i in range(20):
        new = f"r{i}"
        c = c.densify_between(lower, "hi", new)
        lower = new
    assert all(c.rank(n) < Fraction(1) for n in c.ranks if n != "hi")
    assert len(c.ranks) == 22  # lo, hi, + 20 exact rungs, no collisions


def test_densify_rejects_duplicate_name():
    c = Continuum(name="x", ranks={"a": 0, "b": 1}, invariant="x")
    with pytest.raises(ContinuumError):
        c.densify_between("a", "b", "a")  # "a" already exists


def test_from_groupable_materializes_degenerate_continuum():
    g = Groupable.unified("loaded", meaning="loading")
    c = Continuum.from_groupable(g)
    assert isinstance(c, Continuum)
    assert set(c.ranks) == {"not-loaded", "loaded"}
    assert c.rank("not-loaded") == -1 and c.rank("loaded") == 1
    # the materialized continuum's poles recover the bounds (round-trip-ish)
    assert c.poles().minus == "not-loaded" and c.poles().plus == "loaded"
