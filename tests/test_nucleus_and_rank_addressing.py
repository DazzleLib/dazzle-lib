"""C1 (DWP 2026-07-05, bedrock implementation): the Unified nucleus
formalized + ranks as ADDRESSES + subtypes + anonymous rungs + shift.

The user's thesis as pinned vectors: {-1 = remove, 0 = the axis itself
(the nucleus), +1 = add}; 'names are christenings of positions, not
prerequisites'; '0 is the fixed point, always -- whether it is also the
midpoint is a property of the axis's shape'.
"""
from fractions import Fraction

import pytest

from dazzle_lib.groupable import Groupable, Unified
from dazzle_lib.continuum import Continuum, ContinuumError, ContinuumSpace


def membership():
    return Continuum.from_groupable(
        Groupable(minus="remove", plus="add", meaning="membership"))


class TestNucleus:
    def test_the_bridge_roundtrip(self):
        g = Groupable("remove", "add", "membership")
        assert Continuum.from_groupable(g).nucleus() == g.nucleus()

    def test_unified_is_its_own_nucleus(self):
        u = Unified("membership")
        assert u.nucleus() is u

    def test_continuum_nucleus_falls_back_to_name(self):
        c = Continuum("verbosity", ranks={"default": 0, "debug": 1})
        assert c.nucleus().label == "verbosity"

    def test_space_nucleus(self):
        c = membership()
        sp = ContinuumSpace(name="mgmt", meaning="management",
                            axes={"membership": c})
        assert sp.nucleus() == Unified(label="mgmt", meaning="management")

    def test_framing_is_distinct_from_nucleus(self):
        g = Groupable("cold", "hot", "temperature")
        assert g.nucleus().label == "temperature"   # what is conserved
        assert g.framing() == "hot"                 # the default reading
        assert g.framing("cold") == "cold"          # the other reading


class TestLevelAt:
    def test_the_users_thesis(self):
        c = membership()
        assert c.level_at(+1) == "add"
        assert c.level_at(-1) == "remove"

    def test_vacant_rank_raises_with_occupancy(self):
        with pytest.raises(ContinuumError, match="no rung at rank"):
            membership().level_at(0)

    def test_nearest_ties_go_warmer(self):
        assert membership().level_at(0, nearest=True) == "add"

    def test_fraction_ranks_exact(self):
        c = membership().densify_between("remove", "add", "suspended")
        assert c.level_at(Fraction(0, 1)) == "suspended"


class TestSubtypes:
    def test_full_requires_both_reaches(self):
        Continuum("t", ranks={"c": -1, "h": 1}, subtype="full")  # ok
        with pytest.raises(ContinuumError, match="BOTH sides"):
            Continuum("t", ranks={"a": 0, "b": -1}, subtype="full")

    def test_monopole_requires_one_reach(self):
        Continuum("v", ranks={"visible": 0, "hidden": -2},
                  subtype="monopole")  # ok
        with pytest.raises(ContinuumError, match="one reach"):
            Continuum("v", ranks={"a": -1, "b": 1}, subtype="monopole")

    def test_list_is_free_and_unknown_rejected(self):
        Continuum("l", ranks={"add": 0, "remove": -1}, subtype="list")  # ok
        with pytest.raises(ContinuumError, match="unknown subtype"):
            Continuum("x", ranks={"a": 0}, subtype="banana")

    def test_undeclared_stays_legacy_compatible(self):
        Continuum("legacy", ranks={"warm": 0, "cold": -1})  # no rules


class TestAnonymousRungs:
    def test_self_naming(self):
        c = membership().densify_between("remove", "add")
        assert c.rank("0") == Fraction(0, 1)  # the index IS the name

    def test_left_spine_is_the_users_1_over_1_plus_n(self):
        c = Continuum("unit", ranks={"zero": 0, "one": 1})
        upper = "one"
        for n in range(1, 5):
            c = c.densify_between("zero", upper)
            upper = c.rank_name(Fraction(1, n + 1))
            assert c.rank(upper) == Fraction(1, n + 1)

    def test_christening_moves_name_keeps_rank(self):
        c = membership().densify_between("remove", "add")
        c2 = c.rename_level("0", "suspended")
        assert c2.rank("suspended") == Fraction(0, 1)
        assert "0" not in c2.ranks

    def test_densify_carries_fibers(self):
        inner = Continuum("i", ranks={"x": 0})
        c = Continuum("o", ranks={"a": -1, "b": 1}, fibers={"a": inner})
        c2 = c.densify_between("a", "b")
        assert c2.fibers["a"] is inner  # the pre-C1 latent drop, fixed


class TestShift:
    def ladder(self):
        return Continuum("verbosity", ranks={
            "nothing": -4, "default": 0, "timing": 1, "config": 2,
            "debug": 3})

    def test_make_room_names_carry_identity(self):
        c2, remap = self.ladder().shift_from(3, by=1)
        assert c2.rank("debug") == 4          # moved
        assert c2.rank("config") == 2         # untouched
        assert remap == {"debug": (Fraction(3), Fraction(4))}

    def test_moving_the_invariant_seat_is_forbidden(self):
        with pytest.raises(ContinuumError, match="invariant seat"):
            self.ladder().shift_from(0, by=1)

    def test_crossing_the_invariant_is_forbidden(self):
        with pytest.raises(ContinuumError, match="across the invariant"):
            self.ladder().shift_from(1, by=-2)  # timing 1 -> -1

    def test_anonymous_rungs_rekey_on_shift(self):
        c = self.ladder().densify_between("config", "debug")  # "5/2"
        c2, remap = c.shift_from(Fraction(5, 2), by=1)
        assert "5/2" not in c2.ranks
        assert c2.rank("7/2") == Fraction(7, 2)   # re-keyed (the MOVE)
        assert remap["7/2"] == (Fraction(5, 2), Fraction(7, 2))

    def test_gate_semantics_survive_fractions_and_shift(self):
        # E1-E3 promoted: insert, chain, gate at a fractional threshold
        c = self.ladder().densify_between("config", "debug", "tracing")
        c = c.densify_between("config", "tracing", "io-detail")   # 7/3
        threshold = c.rank("io-detail")
        shown = [n for n in c.levels() if c.rank(n) <= threshold]
        assert shown[-1] == "io-detail" and "tracing" not in shown
