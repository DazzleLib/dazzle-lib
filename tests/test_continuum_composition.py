"""The closed-composition algebra laws -- ContinuumSpace is functionally complete.

Gates the closure DWP (2026-06-18__05-10-56): {Continuum, ContinuumSpace, compose}
is complete the way {+, x, ^} is -- compose is CLOSED (a product of products is a
product) and normal_form FOLDS nesting back to a flat leaf product, so arbitrary
dimensions need only three constructs. Alignment (a merged presence spectrum) is a
per-(sub-)space PROPERTY, not a requirement; product spaces refuse cross-axis
navigation by design (scale-safety). The pre-build spike
(dazzlecmd tests/one-offs/arithmetic_as_continuumspace_completeness.py) validated the
MODEL; this validates the BUILT algebra (the standing end-of-build requirement).
"""

import pytest

from dazzle_lib.continuum import Continuum, ContinuumSpace, ContinuumError


def _c(name):
    return Continuum(name=name, ranks={"cold": -1, "zero": 0, "warm": 1})


# --- AC-closure ------------------------------------------------------------
def test_compose_returns_a_space_and_a_member_may_be_a_space():
    inner = ContinuumSpace.compose("inner", {"a": _c("a"), "b": _c("b")})
    outer = ContinuumSpace.compose("outer", {"sub": inner, "c": _c("c")})
    assert isinstance(outer, ContinuumSpace)
    assert isinstance(outer.axes["sub"], ContinuumSpace)   # recursion: space-in-space
    assert not outer.is_aligned                            # a product, no merged spectrum


def test_compose_rejects_empty():
    with pytest.raises(ContinuumError):
        ContinuumSpace.compose("empty", {})


# --- AC-fold / associativity ----------------------------------------------
def test_normal_form_folds_nesting_to_leaf_product():
    a, b, c = _c("a"), _c("b"), _c("c")
    nested = ContinuumSpace.compose("o", {"lower": ContinuumSpace.compose("l", {"a": a, "b": b}), "c": c})
    leaves = nested.normal_form().axes
    assert set(leaves) == {"lower.a", "lower.b", "c"}      # qualified leaf names
    assert all(isinstance(x, Continuum) for x in leaves.values())


def test_associativity_nesting_order_is_presentation_only():
    a, b, c = _c("a"), _c("b"), _c("c")
    left = ContinuumSpace.compose("L", {"ab": ContinuumSpace.compose("ab", {"a": a, "b": b}), "c": c})
    right = ContinuumSpace.compose("R", {"a": a, "bc": ContinuumSpace.compose("bc", {"b": b, "c": c})})
    # the LEAF SET is the invariant (names differ by nesting path; the continua match)
    assert {v.name for v in left.normal_form().axes.values()} == \
           {v.name for v in right.normal_form().axes.values()} == {"a", "b", "c"}


def test_arbitrary_recursion_depth_still_folds():
    leaves = {"x": _c("x")}
    sp = ContinuumSpace.compose("d0", dict(leaves))
    for i in range(5):                                     # nest 5 levels deep
        sp = ContinuumSpace.compose(f"d{i+1}", {"deeper": sp, f"y{i}": _c(f"y{i}")})
    flat = sp.normal_form()
    assert len(flat.axes) == 6                             # x + y0..y4
    assert all(isinstance(v, Continuum) for v in flat.axes.values())


# --- AC-identity / idempotence --------------------------------------------
def test_flat_space_normal_forms_to_itself_idempotent():
    flat = ContinuumSpace.compose("flat", {"a": _c("a"), "b": _c("b")})
    assert flat.normal_form() is flat                      # already flat -> identity
    nf = ContinuumSpace.compose("o", {"s": flat, "c": _c("c")}).normal_form()
    assert set(nf.normal_form().axes) == set(nf.axes)      # idempotent


# --- AC-alignment-locality / scale-safety ---------------------------------
def test_product_space_refuses_cross_axis_navigation():
    prod = ContinuumSpace.compose("p", {"a": _c("a"), "b": _c("b")})
    for op in ("spectrum", "colder_than", "warmer_than", "presence_of", "cascade_to_neutral"):
        with pytest.raises(ContinuumError):
            if op == "spectrum":
                prod.spectrum()
            elif op == "presence_of":
                prod.presence_of("a", "warm")
            elif op == "cascade_to_neutral":
                prod.cascade_to_neutral("a", "warm")
            else:
                getattr(prod, op)("a", "warm")


def test_aligned_space_still_navigates_backcompat():
    a = _c("a")
    aligned = ContinuumSpace(name="al", axes={"a": a},
                             presence={"a": {"cold": -1, "zero": 0, "warm": 1}})
    assert aligned.is_aligned
    assert aligned.spectrum() == (("a", "warm"), ("a", "cold"))   # warm -> cold
    assert aligned.presence_of("a", "cold") == -1


def test_aligned_space_rejects_a_subspace_axis():
    inner = ContinuumSpace.compose("inner", {"a": _c("a")})
    with pytest.raises(ContinuumError):
        # presence given => aligned => axes must be Continuums, not sub-spaces
        ContinuumSpace(name="bad", axes={"sub": inner}, presence={"sub": {}})
