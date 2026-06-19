"""Tests for the ladder floor: ``Unified`` (0_ag) + ``Groupable`` (the {-,+} dual).

Ports the invertibility-floor claims (spike C11 + the value parts of C1) from
dazzlecmd's ``tests/one-offs/latent_recursion_groupable_continuum_space_spike.py``.
The principle under test: invertibility is the FLOOR -- every value is a dual,
nothing is one-way, and a "label" is the unified (0_ag) FORM of a dual, never an
escape from it.
"""
from dazzle_lib import Groupable, Unified


def test_groupable_inverts():
    g = Groupable(minus="not-on", plus="on")
    assert g.invert() == Groupable(minus="on", plus="not-on")


def test_double_inversion_round_trips():
    # -(-(x)) == x
    g = Groupable.unified("on")
    assert g.invert().invert() == g


def test_unified_constructor_derives_inverse():
    g = Groupable.unified("on")
    assert g.plus == "on" and g.minus == "not-on"
    # the cheap form is still a full dual (not a one-way escape)
    assert g.invert() != g


def test_unified_is_implicitly_a_groupable():
    # even a one-pole-looking concept (print) cuts into a dual (print / not-print)
    u = Unified("print")
    g = u.groupable()
    assert isinstance(g, Groupable)
    assert g.plus == "print" and g.minus == "not-print"


def test_unified_invert_is_symmetric():
    # the pre-cut superposition has no chosen direction -> inverting returns itself
    u = Unified("print")
    assert u.invert() == u


def test_meaning_is_optional_and_carried():
    g = Groupable.unified("on", meaning="power")
    assert g.meaning == "power"
    assert g.invert().meaning == "power"  # inversion preserves the unifying concept
    bare = Groupable(minus="a", plus="b")
    assert bare.meaning == ""  # well-formed without a meaning
