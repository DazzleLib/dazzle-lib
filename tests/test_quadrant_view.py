"""Tests for the SH pairwise ``QuadrantView`` on ``ContinuumSpace`` (Step 3).

Ports spike C7 (two channels -> 4 quadrants + diagonals), C8 (the four-phase
orbit + the "absent primitive = hidden phase" recipe, reproduced on the PVIR
mapping), and C9 (the tau-step L,M,L,M flip alternation).
"""
import pytest

from dazzle_lib import Continuum, ContinuumError, ContinuumSpace


def _pair(name1: str, name2: str) -> ContinuumSpace:
    a = Continuum(name=name1, ranks={"-": -1, "+": 1}, invariant=name1)
    b = Continuum(name=name2, ranks={"-": -1, "+": 1}, invariant=name2)
    return ContinuumSpace(name="space", axes={name1: a, name2: b})


def test_quadrants_are_four_sign_combos():
    qv = _pair("exigency", "consumption").quadrants("exigency", "consumption")
    quads = qv.quadrants()
    assert len(quads) == 4 and len(set(quads)) == 4
    assert set(quads) == {(1, 1), (-1, 1), (-1, -1), (1, -1)}


def test_diagonals():
    qv = _pair("a", "b").quadrants("a", "b")
    assert qv.agreement_diagonal() == ("Q2", "Q4")
    assert qv.disagreement_diagonal() == ("Q1", "Q3")


def test_hidden_recipe_absent_primitive():
    # axis1=exigency is the first (M) channel, axis2=consumption the second (L)
    qv = _pair("exigency", "consumption").quadrants("exigency", "consumption")
    assert qv.hidden_at("Q1") == "-"
    assert qv.hidden_at("Q2") == "consumption"   # the L (second) channel
    assert qv.hidden_at("Q3") == "+"
    assert qv.hidden_at("Q4") == "exigency"      # the M (first) channel


def test_pvir_recipe_reproduced():
    # map +->P, -->R, axis1(M)->V, axis2(L)->I; hidden must match the PVIR wheel
    qv = _pair("V", "I").quadrants("V", "I")
    pvir = {"+": "P", "-": "R", "V": "V", "I": "I"}
    hidden = {q: pvir[qv.hidden_at(q)] for q in ("Q1", "Q2", "Q3", "Q4")}
    assert hidden == {"Q1": "R", "Q2": "I", "Q3": "P", "Q4": "V"}


def test_tau_steps_alternate_single_channel():
    qv = _pair("exigency", "consumption").quadrants("exigency", "consumption")
    flips = qv.tau_steps()
    assert flips == ("consumption", "exigency", "consumption", "exigency")  # L,M,L,M
    assert len(set(flips)) == 2  # exactly two channels, alternating


def test_quadrants_rejects_bad_or_duplicate_axes():
    sp = _pair("exigency", "consumption")
    with pytest.raises(ContinuumError):
        sp.quadrants("exigency", "nope")
    with pytest.raises(ContinuumError):
        sp.quadrants("exigency", "exigency")
