"""``dazzle_lib.groupable`` -- the ``{-, +}`` dual and the 0_ag unified value:
the bottom two rungs of the recursive ladder
``Unified -> Groupable -> Continuum -> ContinuumSpace``.

**PURE + import-clean BY CHARTER** (stdlib only, no I/O, no effects), like
:mod:`dazzle_lib.continuum`.

A **Groupable** is the irreducible DUAL: a ``{minus, plus}`` pair sharing one
``meaning``. It is the BOUNDS (the two poles, ``+/- r``) of a Continuum -- the
always-present *extrema role* -- and the unit of INVERTIBILITY: every value in
the system is a Groupable so that nothing is one-way (a switch with only an
"on" action is incoherent; even ``print`` implies ``clear``).

A **Unified** is the 0_ag pre-cut form: a single ``label`` that is IMPLICITLY a
Groupable (``groupable()`` performs the cut, *deriving* the inverse rather than
storing it). It is the cheap representation -- still a full dual, never an
escape from invertibility. ``-(-(x)) == x``: double inversion round-trips.

Grounded in D. Darcy's SH-Mechanics ("an axis is the unification of its two
poles"); validated by the latent-recursion spike (C1, C11). The ``densify()``
bridge up to a :class:`~dazzle_lib.continuum.Continuum` lands with the Continuum
rework (it would couple this module to that one); here the two value types stay
self-contained.
"""
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Unified", "Groupable"]


@dataclass(frozen=True)
class Groupable:
    """The ``{minus, plus}`` dual sharing one ``meaning`` -- the bounds of an axis.

    ``meaning`` is the single concept the two poles are two forms of (the SH
    "axis = unification of its two poles"); it is optional so a bare ``{-, +}``
    pair is still well-formed.
    """

    minus: str
    plus: str
    meaning: str = ""

    def invert(self) -> "Groupable":
        """Swap the poles. EVERY Groupable inverts -- there is no one-way value."""
        return Groupable(minus=self.plus, plus=self.minus, meaning=self.meaning)

    @staticmethod
    def unified(label: str, *, meaning: str = "") -> "Groupable":
        """Build a Groupable from a single UNIFIED (0_ag) label: the inverse is
        DERIVED (``not-<label>``), not stored. The cheap default form -- still a
        full dual, never a one-way escape from invertibility."""
        return Groupable(minus=f"not-{label}", plus=label, meaning=meaning or label)


@dataclass(frozen=True)
class Unified:
    """A 0_ag / unified concept: a single ``label`` BEFORE the cut, IMPLICITLY a
    Groupable.

    Just as a Continuum implicitly carries a ContinuumSpace, a unified value
    implicitly carries its Groupable. The ``label`` is the unified FORM of a
    dual, never an escape from invertibility.
    """

    label: str
    meaning: str = ""

    def groupable(self) -> Groupable:
        """The implicit cut ``0_ag -> {minus, plus}`` (the inverse is derived)."""
        return Groupable.unified(self.label, meaning=self.meaning)

    def invert(self) -> "Unified":
        """The pre-cut superposition is symmetric: inverting a unified value
        (before any direction is chosen) returns itself. The ``-(-(x)) == x``
        round-trip lives on the cut form (see :meth:`Groupable.invert`)."""
        return self
