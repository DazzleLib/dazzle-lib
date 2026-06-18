"""Foundation smoke for the lifted state-system primitives (``dazzle_lib.states``).

Covers the generic machinery in isolation -- no consumer registry. The exhaustive
behavioral suite lives with the consumer that declares real axes (dazzlecmd's
``tests/test_states.py``); this pins that the primitives travel correctly with
the lift (B3b) and that their contracts (the criticality guards, the round-trip
identity) hold in the bedrock.
"""

import pytest

from dazzle_lib.continuum import Continuum
from dazzle_lib.states import (
    OPEN,
    CompositeTransition,
    EntityState,
    Reversibility,
    StateAxis,
    Transition,
    TransitionRegistry,
    assert_round_trip,
    observe,
)


class TestStateAxis:
    def test_fixed_value_set_admits_and_rejects(self):
        axis = StateAxis(name="mode", values=("a", "b"))
        assert axis.admits("a")
        assert not axis.admits("z")

    def test_open_axis_admits_anything(self):
        axis = StateAxis(name="routing", values=None)
        assert axis.admits("any:fqcn")
        assert axis.admits(42)

    def test_continuum_backed_axis_derives_its_values(self):
        c = Continuum(name="v", ranks={"hi": 0, "lo": -1})
        axis = StateAxis(name="v", continuum=c)
        # values DERIVE from the continuum (warm->cold), single source.
        assert set(axis.values) == {"hi", "lo"}

    def test_continuum_values_disagreement_is_a_breach(self):
        c = Continuum(name="v", ranks={"hi": 0, "lo": -1})
        with pytest.raises(ValueError):
            StateAxis(name="v", values=("hi", "MISMATCH"), continuum=c)


class TestEntityState:
    def test_equality_and_subset_restriction(self):
        s = EntityState("x:y", {"mode": "a", "vis": "visible"})
        assert s["mode"] == "a"
        assert s.get("missing", "d") == "d"
        # `on` restricts to a subset of axes (round-trip ignores untouched axes).
        assert s.on("mode") == EntityState("x:y", {"mode": "a"})
        assert s.on("mode") != s


class TestTransition:
    def test_generative_must_declare_creates_or_loses(self):
        with pytest.raises(ValueError):
            Transition(axis="k", from_values=("t",), to_value=OPEN, verb="g",
                       reversibility=Reversibility.GENERATIVE)

    def test_reversible_must_preserve_fqcn(self):
        with pytest.raises(ValueError):
            Transition(axis="k", from_values=(OPEN,), to_value=OPEN, verb="r",
                       reversibility=Reversibility.REVERSIBLE, fqcn_fate="reborn")

    def test_matches_honors_verb_axis_and_wildcards(self):
        t = Transition(axis="mode", from_values=("a", "b"), to_value=OPEN, verb="rebind",
                       reversibility=Reversibility.REVERSIBLE, conserved="url")
        assert t.reversible
        assert t.matches(verb="rebind", axis="mode", from_value="a")
        assert not t.matches(verb="rebind", axis="mode", from_value="z")
        assert not t.matches(verb="other", axis="mode", from_value="a")


class TestCompositeTransition:
    def test_interaction_makes_the_whole_generative(self):
        # leg1 CREATES "remote" which leg2 CONSERVES -> generative even though
        # each leg in isolation is weaker.
        leg1 = Transition(axis="kind", from_values=("tool",), to_value=OPEN, verb="grad",
                          reversibility=Reversibility.GENERATIVE, conserved="files",
                          creates=("remote",), loses=("coupling",), fqcn_fate="reborn")
        leg2 = Transition(axis="mode", from_values=("embedded",), to_value="submodule",
                          verb="grad", reversibility=Reversibility.ONE_WAY, conserved="remote")
        comp = CompositeTransition(name="graduation", legs=(leg1, leg2), verb="grad")
        assert comp.reversibility is Reversibility.GENERATIVE
        assert "remote" in comp.creates
        assert comp.axes == ("kind", "mode")

    def test_strongest_leg_when_no_interaction(self):
        leg1 = Transition(axis="a", from_values=(OPEN,), to_value=OPEN, verb="v",
                          reversibility=Reversibility.REVERSIBLE)
        leg2 = Transition(axis="b", from_values=(OPEN,), to_value=OPEN, verb="v",
                          reversibility=Reversibility.ONE_WAY)
        comp = CompositeTransition(name="c", legs=(leg1, leg2), verb="v")
        assert comp.reversibility is Reversibility.ONE_WAY

    def test_empty_legs_rejected(self):
        with pytest.raises(ValueError):
            CompositeTransition(name="c", legs=(), verb="v")


class TestTransitionRegistry:
    def _reg(self):
        reg = TransitionRegistry()
        reg.register_axis(StateAxis(name="mode", values=("a", "b")))
        reg.declare(Transition(axis="mode", from_values=("a",), to_value="b", verb="rebind",
                               reversibility=Reversibility.REVERSIBLE, conserved="url"))
        return reg

    def test_declare_validates_endpoints_against_axis(self):
        reg = self._reg()
        with pytest.raises(ValueError):
            reg.declare(Transition(axis="mode", from_values=("ZZZ",), to_value="b", verb="x",
                                   reversibility=Reversibility.REVERSIBLE))

    def test_declare_unknown_axis_raises(self):
        reg = TransitionRegistry()
        with pytest.raises(KeyError):
            reg.declare(Transition(axis="ghost", from_values=(OPEN,), to_value=OPEN, verb="x",
                                   reversibility=Reversibility.REVERSIBLE))

    def test_lookup_and_by_reversibility(self):
        reg = self._reg()
        t = reg.lookup(verb="rebind", axis="mode", from_value="a")
        assert t.to_value == "b"
        assert reg.by_reversibility(Reversibility.REVERSIBLE) == (t,)
        assert reg.by_reversibility(Reversibility.GENERATIVE) == ()
        with pytest.raises(LookupError):
            reg.lookup(verb="rebind", axis="mode", from_value="nope")


class TestRoundTripAndObserve:
    def test_round_trip_identity_passes_and_violation_raises(self):
        # a tiny in-memory cell: apply flips it, invert flips it back.
        cell = {"v": "a"}
        assert_round_trip(
            read=lambda: cell["v"],
            apply=lambda: cell.update(v="b") or "receipt",
            invert=lambda _r: cell.update(v="a"),
        )
        # an invert that does NOT restore must be caught.
        with pytest.raises(AssertionError):
            assert_round_trip(
                read=lambda: cell["v"],
                apply=lambda: cell.update(v="b") or "receipt",
                invert=lambda _r: None,  # forgot to restore
            )

    def test_observe_validates_against_registered_axes(self):
        reg = TransitionRegistry()
        reg.register_axis(StateAxis(name="mode", values=("a", "b")))
        s = observe(reg, "x:y", mode="a")
        assert s["mode"] == "a"
        with pytest.raises(ValueError):
            observe(reg, "x:y", mode="ZZZ")        # value not admitted
        with pytest.raises(KeyError):
            observe(reg, "x:y", ghost="a")          # axis not registered
