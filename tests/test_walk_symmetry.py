"""The unified inward/outward traversal: ``children`` / ``walk`` / ``fold``.

Ports the symmetry spike: ONE traversal descends a ContinuumSpace's axes
(OUTWARD) AND a Continuum's per-rung fibers (INWARD) identically -- direction is
not special. The behavior-preservation guard: leaves-via-walk == the shipped
ContinuumSpace.leaves() on the axes-only case.
"""
from dazzle_lib import (
    Continuum,
    ContinuumSpace,
    Groupable,
    Unified,
    children,
    fold,
    walk,
)


def _outward() -> ContinuumSpace:
    a = Continuum("a", {"-": -1, "+": 1})
    b = Continuum("b", {"-": -1, "+": 1})
    sub = ContinuumSpace(name="sub", axes={"a": a, "b": b})
    c = Continuum("c", {"-": -1, "+": 1})
    return ContinuumSpace(name="outer", axes={"sub": sub, "c": c})


def _inward() -> Continuum:
    kit = ContinuumSpace(name="kit", axes={"vis": Continuum("vis", {"-": -1, "+": 1})})
    return Continuum(
        "membership", {"pointer": -1, "loaded": 1},
        fibers={"pointer": Unified("src"), "loaded": kit},
    )


def test_children_total_over_ladder():
    for n in (Unified("u"), Groupable("-", "+"),
              Continuum("c", {"-": -1, "+": 1}), _outward()):
        assert isinstance(children(n), dict)


def test_walk_descends_axes_outward():
    nodes = [type(n).__name__ for _, n in walk(_outward())]
    assert nodes.count("Continuum") == 3 and nodes.count("ContinuumSpace") == 2


def test_walk_descends_fibers_inward():
    keys = {k for k, _ in walk(_inward())}
    assert ("pointer",) in keys           # the pointer fiber (a Unified)
    assert ("loaded",) in keys            # the loaded fiber (a sub-space)
    assert ("loaded", "vis") in keys      # DEEP inward: the kit's own axis


def test_unfibered_continuum_is_a_leaf():
    # byte-transparent default: no fibers -> no children
    assert children(Continuum("x", {"-": -1, "+": 1})) == {}


def test_leaves_via_walk_matches_shipped_leaves():
    sp = _outward()
    via_walk = sorted(n.name for _, n in walk(sp) if not children(n))
    shipped = sorted(c.name for c in sp.leaves().values())
    assert via_walk == shipped == ["a", "b", "c"]


def test_fold_collects_leaf_names():
    names = fold(
        _outward(),
        leaf=lambda n: [getattr(n, "name", "?")],
        combine=lambda n, kids: sum(kids, []),
    )
    assert sorted(names) == ["a", "b", "c"]
