"""Tests for the Step-2 ladder bridges on ``Continuum``:
``poles()``, ``densify_between()``, ``from_groupable()``.

Ports spike C1 (poles -> Groupable) + C2 (exact mediant densification) from
dazzlecmd's latent-recursion spike. The production ``Continuum`` stays
NAME-keyed; densification adds Fraction-positioned named rungs without touching
existing int rungs (byte-transparent).
"""
from fractions import Fraction

import pytest

from dazzle_lib import (
    Continuum,
    ContinuumError,
    ContinuumSpace,
    Groupable,
    GroupableProtocol,
    Unified,
    promote,
)


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


# ---------------------------------------------------------------------------
# Value-ladder closure laws (value-ladder-closure DWP, T1).
#
# The bidirectional morphism ladder ``Unified <-> Groupable <-> Continuum <->
# ContinuumSpace``: reduce (``unify`` / ``flatten`` / ``axis``) is total +
# deductive; promote (``cut`` / ``from_groupable`` / ``compose``) is a choice.
# ``reduce . promote == id`` on canonical inputs; ``promote . reduce`` is
# intentionally lossy (a retraction, not an isomorphism). Seeded from the spike
# ``spike_groupable_continuum_ladder.py`` (15/15).
# ---------------------------------------------------------------------------


def test_unify_reduces_a_groupable_to_its_unifying_axis():
    g = Groupable.unified("loaded", meaning="loading")
    u = g.unify()
    assert isinstance(u, Unified)
    assert u.label == "loading"          # the axis = the `meaning` (the SH cut)
    assert u.meaning == "loading"


def test_unify_then_groupable_round_trips():            # AC-V1
    # The round-trip holds for a canonical unified-origin dual (plus == meaning,
    # minus == "not-<axis>"); a dual whose pole label differs from its axis is
    # not unified-origin and reduce is intentionally lossy there.
    g = Groupable.unified("activation")
    assert g.unify().groupable() == g


def test_cut_then_unify_recovers_the_axis_label():     # AC-V1, the user's law
    u = Unified(label="activation")
    assert u.groupable().unify().label == u.label


def test_unify_falls_back_to_the_plus_pole_without_a_meaning():
    g = Groupable(minus="off", plus="on")              # non-unified-origin dual
    assert g.unify().label == "on"


def test_flatten_is_the_named_alias_of_poles():
    c = _ladder()
    assert c.flatten() == c.poles()


def test_flatten_ignores_added_middle_rungs():         # AC-V2
    g = Groupable.unified("on", meaning="activation")
    c = Continuum.from_groupable(g)
    densified = c.densify_between("not-on", "on", "half")
    assert densified.flatten() == c.flatten() == g


def test_from_groupable_then_flatten_round_trips():     # AC-V1
    g = Groupable.unified("on", meaning="activation")
    assert Continuum.from_groupable(g).flatten() == g


def test_densify_at_center_materializes_the_hidden_zero():   # AC-V3
    g = Groupable.unified("on", meaning="activation")
    c = Continuum.from_groupable(g).densify_between("not-on", "on", "neutral")
    assert c.rank("neutral") == 0          # mediant(-1, +1) == 0
    assert c.neutral() == "neutral"        # the 3-rung/odd case has an explicit 0


def test_promote_steps_one_rung_up_the_whole_ladder():
    u = Unified(label="activation")
    g = promote(u)
    assert isinstance(g, Groupable) and g == u.groupable()
    c = promote(g)
    assert isinstance(c, Continuum) and c == Continuum.from_groupable(g)
    space = promote(c)
    assert isinstance(space, ContinuumSpace)
    assert space.axes[c.name] == c         # the single composed axis is recoverable


def test_promote_then_reduce_is_a_retraction_on_the_dual():   # L2
    g = Groupable.unified("on", meaning="activation")
    assert promote(g).flatten() == g       # Groupable -> Continuum -> Groupable


def test_groupable_satisfies_the_groupable_protocol():   # AC-V6
    # The bedrock value conforms to its value-LOCAL structural contract unchanged
    # (the contract a consumer accepts when it means "a {P, not-P} dual").
    assert isinstance(Groupable.unified("on", meaning="activation"), GroupableProtocol)
    assert isinstance(Groupable("off", "on"), GroupableProtocol)
