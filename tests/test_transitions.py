"""Foundation smoke for the lifted transition executor (``dazzle_lib.transitions``).

Exercises the generic engine in isolation against a hand-built registry + plain
in-memory substrate. The exhaustive per-verb behavior lives with the consumer
that binds real substrates (dazzlecmd's groupable/visibility/containment tests);
this pins the engine's contract in the bedrock -- crucially that it carries
identity through the ``identity_of`` hook and assumes NOTHING about the entity's
shape (the entities here deliberately have no ``.fqcn``).
"""

import pytest

from dazzle_lib.states import (
    OPEN,
    Reversibility,
    StateAxis,
    Transition,
    TransitionRegistry,
)
from dazzle_lib.transitions import (
    CriticalityBoundaryError,
    Receipt,
    TransitionContext,
    TransitionError,
)


class _Thing:
    """A consumer entity with NO ``.fqcn`` -- proving the executor never assumes it."""
    def __init__(self, name):
        self.name = name


def _registry():
    # The generic executor is for axes with ONE edge per (verb, axis) -- it picks
    # the first such edge and does NOT disambiguate by from_value (multi-edge axes
    # like MODE rebind use their own context). So: one reversible rebind edge.
    reg = TransitionRegistry()
    reg.register_axis(StateAxis(name="mode", values=("a", "b")))
    reg.declare(Transition(axis="mode", from_values=("a", "b"), to_value=OPEN,
                           verb="rebind", reversibility=Reversibility.REVERSIBLE,
                           conserved="url"))
    return reg


def _refusing_registry():
    # A registry whose single rebind edge is REFUSED_AT_BOUNDARY -- the executor's
    # generic pre-flight refusal fires off edges[0].
    reg = TransitionRegistry()
    reg.register_axis(StateAxis(name="mode", values=("a", "b")))
    reg.declare(Transition(axis="mode", from_values=(OPEN,), to_value=OPEN,
                           verb="rebind", reversibility=Reversibility.REFUSED_AT_BOUNDARY,
                           conserved="url"))
    return reg


def _ctx(reg, cell, *, check=None, invert=None):
    return TransitionContext(
        reg, "mode",
        detect=lambda e: cell[e.name],
        write=lambda e, target, prev: cell.__setitem__(e.name, target),
        identity_of=lambda e: f"thing:{e.name}",   # the seam -- no .fqcn anywhere
        check=check, invert=invert,
    )


class TestApply:
    def test_apply_returns_receipt_with_registry_truth(self):
        cell = {"x": "a"}
        r = _ctx(_registry(), cell).apply(_Thing("x"), "b", verb="rebind")
        assert isinstance(r, Receipt)
        # identity flows through identity_of -- NOT through any .fqcn attribute.
        assert r.entity_identity == "thing:x"
        assert r.previous_state == "a" and r.new_state == "b"
        # conserved/reversible are READ FROM the declared edge, not hardcoded.
        assert r.conserved == "url" and r.reversible is True
        assert cell["x"] == "b"   # the write hook ran

    def test_refused_at_boundary_raises_criticality(self):
        cell = {"x": "a"}
        with pytest.raises(CriticalityBoundaryError):
            _ctx(_refusing_registry(), cell).apply(_Thing("x"), "b", verb="rebind")
        assert cell["x"] == "a"   # refused PRE-FLIGHT -- substrate untouched

    def test_unknown_edge_raises_lookup(self):
        cell = {"x": "a"}
        with pytest.raises(LookupError):
            _ctx(_registry(), cell).apply(_Thing("x"), "b", verb="no_such_verb")

    def test_check_hook_can_refuse(self):
        def refuse(entity, target, verb, prev):
            raise CriticalityBoundaryError("policy says no")
        cell = {"x": "a"}
        with pytest.raises(CriticalityBoundaryError, match="policy says no"):
            _ctx(_registry(), cell, check=refuse).apply(_Thing("x"), "b", verb="rebind")


class TestUndo:
    def test_undo_round_trips_to_previous_state(self):
        cell = {"x": "a"}
        ctx = _ctx(_registry(), cell)
        ctx.apply(_Thing("x"), "b", verb="rebind")
        assert cell["x"] == "b"
        ctx.undo(Receipt(entity_identity="thing:x", axis="mode", previous_state="a",
                         new_state="b", conserved="url", reversible=True, verb="rebind"))
        assert cell["x"] == "a"   # restored -- the identity round-trips

    def test_undo_without_apply_raises_transition_error(self):
        cell = {"x": "a"}
        with pytest.raises(TransitionError):
            _ctx(_registry(), cell).undo(
                Receipt(entity_identity="thing:x", axis="mode", previous_state="a",
                        new_state="b", conserved="url", reversible=True, verb="rebind"))
