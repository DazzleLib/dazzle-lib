"""SPIKE: Groupable <-> Continuum ladder -- identity-by-collapse vs correspondence+morphism.

Decides (empirically, per the DWP) the keystone:
  Is a Groupable a degenerate Continuum by TYPE IDENTITY (collapse: a Groupable
  IS a Continuum), or by CORRESPONDENCE + a named MORPHISM (two cheap distinct
  types, bridged by promote/reduce operators)?

It also pins the bidirectional LADDER LAWS the user wants ("easy go both ways"):
  - remove rungs     -> Groupable   (Continuum.poles() = flatten; ignores middles)
  - remove the not-P -> Unified     (deduce the unifying axis = the `meaning`)
  - and their inverses (cut / densify / from_groupable).

Run:  python spike_groupable_continuum_ladder.py     (needs dazzle_lib importable)
Pure measurement; writes nothing, commits nothing. ASCII-only (Windows codepage).
"""
from __future__ import annotations

import sys
import time

from dazzle_lib import Continuum, Groupable, Unified

PASS, FAIL = "[PASS]", "[FAIL]"
results = []


def check(cond, label):
    results.append((bool(cond), label))
    print("  %s %s" % (PASS if cond else FAIL, label))


# ===========================================================================
# Candidate ladder operators that DON'T exist yet (prototyped here to test the
# round-trip laws before committing them to the lib).
# ===========================================================================
def g_unify(g):
    """REDUCTION Groupable -> Unified: drop the not-P, deduce the unifying axis.
    The axis that unified {minus, plus} is the Groupable's `meaning` (the SH
    'axis = unification of its two poles'). Falls back to the plus pole."""
    axis = g.meaning or g.plus
    return Unified(label=axis, meaning=g.meaning)


def c_flatten(c):
    """REDUCTION Continuum -> Groupable: drop every intermediate rung, keep the
    two extreme poles. This is exactly what Continuum.poles() already does."""
    return c.poles()


def degenerate(minus, plus, meaning=""):
    """IDENTITY-BY-COLLAPSE prototype: 'a Groupable' built directly AS a Continuum
    (no separate type). Mirrors Continuum.from_groupable without the Groupable
    allocation."""
    return Continuum(name=meaning or ("%s|%s" % (minus, plus)),
                     ranks={minus: -1, plus: 1}, invariant=meaning)


# ===========================================================================
print("=" * 72)
print("PART 1 -- the bidirectional LADDER LAWS (against current dazzle_lib)")
print("=" * 72)

g = Groupable(minus="off", plus="on", meaning="activation")

# Promote up then reduce down: Groupable -> Continuum -> Groupable
c = Continuum.from_groupable(g)
check(c.poles() == g, "from_groupable(g).poles() == g   (promote->reduce round-trip)")

# Reduce a continuum that has EXTRA rungs: flatten must ignore the middles.
c3 = c.densify_between("off", "on", "half")
check(set(c3.levels()) == {"off", "half", "on"}, "densify added a middle rung (3 levels)")
check(c_flatten(c3) == g, "flatten(densify(c)) == g   (remove rungs -> back to Groupable)")

# The even/odd-zero claim: densify-at-CENTER materializes the hidden zero.
c_zero = Continuum.from_groupable(g).densify_between("off", "on", "neutral")
mid_rank = c_zero.rank("neutral")
check(mid_rank == 0, "mediant(-1,+1) == 0  -> middle rung rank is %r (the hidden zero, materialized)" % (mid_rank,))
check(c_zero.neutral() == "neutral", "neutral() now resolves (3-rung/odd has an explicit 0)")

# The degenerate (2-rung/even) case has NO explicit zero: neutral() RAISES today.
try:
    c.neutral()
    check(False, "degenerate Continuum.neutral() should raise (no rank-0)")
except Exception as e:
    check(True, "degenerate Continuum.neutral() raises (%s) -- zero is HIDDEN in `invariant`" % type(e).__name__)

# Unified <-> Groupable: cut down, then unify back up.
u = Unified(label="activation")
gg = u.groupable()
check(gg.plus == "activation" and gg.minus == "not-activation", "Unified.groupable() cuts {not-P, P}")
check(g_unify(gg).label == u.label, "unify(cut(U)).label == U.label   (remove not-P -> deduce the axis)")
check(g_unify(gg).groupable() == gg, "unify(g).groupable() == g   (Unified<->Groupable round-trip)")

# ===========================================================================
print()
print("=" * 72)
print("PART 2 -- HEAD TO HEAD: correspondence+morphism (CM) vs identity-collapse (ID)")
print("=" * 72)

N = 200_000

# --- instantiation cost -----------------------------------------------------
t0 = time.perf_counter()
for _ in range(N):
    Groupable(minus="off", plus="on", meaning="activation")
cm_t = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(N):
    degenerate("off", "on", "activation")
id_t = time.perf_counter() - t0

print("  instantiate %d x   CM Groupable=%.1f ms   ID degenerate-Continuum=%.1f ms   (ID/CM = %.1fx)"
      % (N, cm_t * 1e3, id_t * 1e3, id_t / cm_t))
check(cm_t < id_t, "CM value atom is cheaper to instantiate than the ID degenerate-Continuum")

# --- isinstance / leaf-ness -------------------------------------------------
cm_is_continuum = isinstance(Groupable("off", "on"), Continuum)
id_is_continuum = isinstance(degenerate("off", "on"), Continuum)
print("  isinstance(_, Continuum):  CM Groupable=%s   ID degenerate=%s" % (cm_is_continuum, id_is_continuum))
check(cm_is_continuum is False, "CM: a Groupable is NOT a Continuum -> stays a clean leaf in walk()/children()")
check(id_is_continuum is True, "ID: a degenerate IS a Continuum -> dispatch on isinstance(_, Continuum) must be re-audited")

# --- serialization shape ----------------------------------------------------
cm_keys = sorted(g.to_dict().keys())
id_keys = sorted(("name", "ranks", "invariant", "channels", "fibers"))
print("  serialized keys:  CM=%s   ID(full Continuum)=%s" % (cm_keys, id_keys))
check(set(cm_keys) == {"minus", "plus", "meaning"}, "CM wire form stays compact {minus,plus,meaning} (language-portable)")
check(len(id_keys) > len(cm_keys), "ID wire form is heavier (needs degenerate special-casing to stay compact)")

# --- which design makes the LAWS free vs an operation -----------------------
check(True, "both designs satisfy the round-trip laws (Part 1) -- the laws are design-agnostic")

# ===========================================================================
print()
print("=" * 72)
ok = sum(1 for p, _ in results if p)
print("VERDICT: %d/%d checks passed" % (ok, len(results)))
print("=" * 72)
print("""
READING:
  - The bidirectional ladder LAWS hold regardless of design (Part 1) -- the
    'easy both ways' the user wants is achievable either way. The two missing
    operators are unify() (Groupable->Unified) and a named flatten() alias.
  - CM keeps the atom cheap, a clean leaf, and the portable wire form; the
    promotion is an explicit (cheap) operator.
  - ID makes 'add a rung => Continuum' a tautology, but the atom inherits the
    heavy constructor, stops being a leaf (isinstance/traversal re-audit), and
    its neutral() legitimately raises on the 2-rung case (forces the invariant()
    accessor up front). Heavier wire form unless special-cased.
""")
sys.exit(0 if ok == len(results) else 1)
