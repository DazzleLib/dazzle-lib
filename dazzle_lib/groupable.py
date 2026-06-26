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
from typing import Any, ClassVar, Dict, Protocol, runtime_checkable

__all__ = ["Unified", "Groupable", "GroupableProtocol"]


@runtime_checkable
class GroupableProtocol(Protocol):
    """The structural contract the bedrock VALUE :class:`Groupable` satisfies --
    its value-LOCAL surface: the ``{minus, plus, meaning}`` dual, ``invert``, the
    serialization round-trip, and the ``unify`` reduction. Mirrors the
    ``ContinuumProtocol`` idiom (nothing is forced to subclass).

    Value-LOCAL on purpose: it does NOT name the promotion (``from_groupable`` /
    ``densify`` live on the Continuum side), so this contract never references
    ``Continuum`` -- the module stays acyclic by charter. This is the type a
    consumer accepts when it means "a {P, not-P} dual", distinct from the entity
    grouping CAPABILITY (``dazzlecmd_lib`` ``GroupingCapable``)."""

    minus: str
    plus: str
    meaning: str
    SCHEMA_VERSION: int

    def invert(self) -> "Groupable": ...
    def unify(self) -> "Unified": ...
    def to_dict(self) -> Dict[str, Any]: ...


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

    SCHEMA_VERSION: ClassVar[int] = 1

    def invert(self) -> "Groupable":
        """Swap the poles. EVERY Groupable inverts -- there is no one-way value."""
        return Groupable(minus=self.plus, plus=self.minus, meaning=self.meaning)

    def unify(self) -> "Unified":
        """REDUCTION ``Groupable -> Unified``: drop the derived not-P pole, keep
        the unifying axis. The axis that unified ``{minus, plus}`` is ``meaning``
        (the SH "axis = the unification of its two poles"); falls back to ``plus``
        when ``meaning`` is empty (a non-unified-origin dual). The inverse of
        :meth:`Unified.groupable` on unified-origin values --
        ``g.unify().groupable() == g`` and ``cut(U).unify().label == U.label``.
        Lives here, not on Continuum: ``Unified`` is co-resident, so the
        reduction stays acyclic (``groupable.py`` imports nothing from
        ``continuum``)."""
        return Unified(label=self.meaning or self.plus, meaning=self.meaning)

    @staticmethod
    def unified(label: str, *, meaning: str = "") -> "Groupable":
        """Build a Groupable from a single UNIFIED (0_ag) label: the inverse is
        DERIVED (``not-<label>``), not stored. The cheap default form -- still a
        full dual, never a one-way escape from invertibility."""
        return Groupable(minus=f"not-{label}", plus=label, meaning=meaning or label)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a tree of basic types (satisfies the ``Serializable``
        protocol; the value object proves it is self-contained)."""
        return {"minus": self.minus, "plus": self.plus, "meaning": self.meaning}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Groupable":
        return cls(
            minus=data["minus"], plus=data["plus"], meaning=data.get("meaning", "")
        )


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

    SCHEMA_VERSION: ClassVar[int] = 1

    def groupable(self) -> Groupable:
        """The implicit cut ``0_ag -> {minus, plus}`` (the inverse is derived)."""
        return Groupable.unified(self.label, meaning=self.meaning)

    def invert(self) -> "Unified":
        """The pre-cut superposition is symmetric: inverting a unified value
        (before any direction is chosen) returns itself. The ``-(-(x)) == x``
        round-trip lives on the cut form (see :meth:`Groupable.invert`)."""
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {"label": self.label, "meaning": self.meaning}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Unified":
        return cls(label=data["label"], meaning=data.get("meaning", ""))
