"""Foundation tests for the Continuum primitive (lifted in 0.3).

A focused smoke over the public surface of `dazzle_lib.continuum`; the deeper
exhaustive suite lives downstream in dazzlecmd (which exercises it via its
re-export shim). This pins the bedrock's own coverage of the primitive.
"""

import pytest

from dazzle_lib.continuum import (
    Continuum,
    ContinuumBoundaryError,
    ContinuumError,
    ContinuumProtocol,
    ContinuumSpace,
    ContinuumSpaceProtocol,
)


def _visibility():
    return Continuum(
        name="visibility",
        ranks={"visible": 0, "silenced": -1, "hidden": -2, "shadowed": -3},
        invariant="canonical_dispatch",
        channels={
            "visible": frozenset(),
            "silenced": frozenset({"hints"}),
            "hidden": frozenset({"hints", "display"}),
            "shadowed": frozenset({"hints", "display", "resolution"}),
        },
    )


class TestContinuum:
    def test_order_poles_neutral(self):
        c = _visibility()
        assert c.levels() == ("shadowed", "hidden", "silenced", "visible")  # cold->warm
        assert c.neutral() == "visible" and c.rank("visible") == 0
        assert c.cold_pole() == "shadowed" and c.warm_pole() == "visible"
        assert c.compare("visible", "shadowed") == 1
        assert c.is_warmer("visible", "hidden") and c.is_colder("shadowed", "hidden")

    def test_step_and_lens(self):
        c = _visibility()
        assert c.step("hidden", +1) == "silenced"      # warmer
        assert c.step("hidden", -1) == "shadowed"       # colder
        with pytest.raises(ContinuumBoundaryError):
            c.step("shadowed", -1)                       # past the cold pole
        # the warm/cold lens duality: warm.more == cold.less
        assert c.warm.more("hidden") == c.cold.less("hidden") == "silenced"

    def test_thac0_gate_and_channels(self):
        c = _visibility()
        assert c.passes("hidden", "silenced") is True   # rank(-2) <= rank(-1)
        assert c.passes("silenced", "hidden") is False
        assert c.channels_at("hidden") == frozenset({"hints", "display"})
        assert c.level_for_channels(frozenset({"display"})) == "hidden"  # highest wins

    def test_rejects_duplicate_ranks(self):
        with pytest.raises(ContinuumError):
            Continuum(name="x", ranks={"a": 0, "b": 0})

    def test_satisfies_protocol(self):
        assert isinstance(_visibility(), ContinuumProtocol)


def _space():
    return ContinuumSpace(
        name="kit_presence", meaning="how present a tool is",
        axes={"visibility": _visibility()},
        presence={"visibility": {"visible": 0, "silenced": -1, "hidden": -2, "shadowed": -3}},
    )


class TestContinuumSpace:
    def test_presence_and_spectrum(self):
        s = _space()
        assert s.presence_of("visibility", "hidden") == -2
        assert s.is_neutral("visibility", "visible")
        assert s.spectrum() == (("visibility", "silenced"), ("visibility", "hidden"),
                                ("visibility", "shadowed"))  # warm->cold, neutral omitted

    def test_navigation(self):
        s = _space()
        assert s.colder_than("visibility", "hidden") == ("visibility", "shadowed")
        assert s.warmer_than("visibility", "hidden") == ("visibility", "silenced")

    def test_slice_and_cascade(self):
        s = _space()
        assert s.slice("visibility", "hidden", lo=-1, hi=2) == (
            "shadowed", "hidden", "silenced", "visible")
        assert s.cascade_to_neutral("visibility", "hidden") == ("hidden", "silenced")
        assert s.cascade_to_neutral("visibility", "visible") == ()

    def test_contract_rejects_misaligned_presence(self):
        with pytest.raises(ContinuumError):
            ContinuumSpace(
                name="bad", axes={"v": _visibility()},
                presence={"v": {"visible": 0, "silenced": -1, "hidden": -1, "shadowed": -3}})  # dup -1

    def test_satisfies_protocol(self):
        assert isinstance(_space(), ContinuumSpaceProtocol)
