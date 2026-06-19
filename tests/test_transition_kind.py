"""Step 4: the lateral/generative vocabulary bridge -- ``Transition.kind``.

The existing ``states.py`` machinery (``EntityState`` as the point, ``Reversibility``,
``creates``/``loses``) IS the State/Transition layer of the redesign. This confirms
the redesign's LATERAL / GENERATIVE vocabulary (spike C13) maps onto it:
lateral = REVERSIBLE (round-trips); generative = GENERATIVE (lossy-on-reverse
unless a Receipt preserves -- so ``creates``/``loses`` MUST be declared).
"""
import pytest

from dazzle_lib import Reversibility, Transition


def test_lateral_kind():
    t = Transition(
        axis="visibility", from_values=("visible",), to_value="hidden",
        verb="hide", reversibility=Reversibility.REVERSIBLE, conserved="presence",
    )
    assert t.kind == "lateral"
    assert t.reversible is True


def test_generative_kind_declares_creates():
    t = Transition(
        axis="materialization", from_values=("absent",), to_value="present",
        verb="materialize", reversibility=Reversibility.GENERATIVE,
        creates=("local_files",), identity_fate="reborn",
    )
    assert t.kind == "generative"
    assert t.reversible is False
    assert t.creates == ("local_files",)  # the criticality is explicit data


def test_generative_requires_creates_or_loses():
    # a generative edge with nothing declared is rejected at construction
    with pytest.raises(Exception):
        Transition(
            axis="x", from_values=("a",), to_value="b", verb="v",
            reversibility=Reversibility.GENERATIVE,
        )


def test_refused_kind():
    t = Transition(
        axis="x", from_values=("a",), to_value="b", verb="v",
        reversibility=Reversibility.REFUSED_AT_BOUNDARY,
    )
    assert t.kind == "refused"


def test_one_way_kind():
    # ONE_WAY = permitted but cannot return on its own (a mini-graduation,
    # e.g. embedded -> publish). Surfaced by the consumer-integration probe:
    # the real registry declares ONE_WAY edges that an incomplete kind() missed.
    t = Transition(
        axis="mode", from_values=("embedded",), to_value="published",
        verb="publish", reversibility=Reversibility.ONE_WAY,
    )
    assert t.kind == "one-way"
    assert t.reversible is False


def test_kind_covers_every_reversibility():
    # COMPLETENESS GUARD: every Reversibility value must have a kind mapping, so a
    # newly-added enum member without one fails here (no silent fallback).
    valid = {"lateral", "one-way", "generative", "refused"}
    for r in Reversibility:
        kwargs = dict(axis="x", from_values=("a",), to_value="b", verb="v", reversibility=r)
        if r is Reversibility.GENERATIVE:
            kwargs.update(creates=("thing",), identity_fate="reborn")
        assert Transition(**kwargs).kind in valid
