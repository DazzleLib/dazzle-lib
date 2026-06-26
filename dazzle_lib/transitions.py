"""The generic transition executor -- one engine for any declared state axis.

A :class:`TransitionContext` runs the same dance every effectful state-transition
does: read the entity's current value off its substrate, resolve the DECLARED
edge for the verb (so the :class:`Receipt` reports the registry's reversibility /
conserved invariant rather than a hardcoded literal), refuse it if it crosses a
criticality boundary, write the substrate, and return a receipt. The per-axis
substrate I/O + policy are small consumer-supplied hooks bound to a handle, so
the declared registry (``dazzle_lib.states``) stays pure -- it DECLARES the axes;
the consumer reads/writes them.

Lifted to the dazzle-lib bedrock (B3c of dazzlecmd's Groupable<->Continuum<->
states unification; dazzle-lib 0.5.0). The executor proved generic over an
INJECTED registry + hooks -- its one coupling to a consumer was an ``entity.fqcn``
attribute access, now a domain-neutral ``identity_of`` hook (the same shape as the
``detect``/``write`` hooks). dazzlecmd's per-verb contexts (alias rebind, mode
switch, visibility, containment, projection) BIND this executor to their
substrates; they stay in the consumer.

**PURE BY CHARTER.** stdlib + :mod:`dazzle_lib.states` (``Reversibility``) only --
no I/O, no effects. The effectful substrate work lives in the consumer-supplied
hooks, never here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Protocol, runtime_checkable

from .states import Reversibility


class CriticalityBoundaryError(Exception):
    """Raised when a transition would cross a criticality boundary.

    The conserved invariant cannot be preserved, so the transition would be
    irreversible/non-restorable -- it is refused rather than performed.

    Example: a mode-switch ``rebind`` whose published state cannot be re-derived
    (no remote URL resolvable) would be a lossy, unrecoverable change.

    This is a PRE-FLIGHT refusal (the invariant check fails before any change).
    """


class TransitionError(Exception):
    """Raised when a transition fails to APPLY.

    Distinct from :class:`CriticalityBoundaryError` (a pre-flight refusal): the
    invariant was fine, but the underlying mechanism failed mid-apply (e.g. a
    substrate write returned a non-zero exit code, or ``undo`` was called with no
    prior ``apply``). The transition's success/failure is the mechanism's; this
    surfaces it as the executor's typed failure.
    """


@dataclass(frozen=True)
class Receipt:
    """The generic record one transition leaves -- the collapse of the per-verb
    ``*Receipt`` types.

    ``conserved`` (the conserved-invariant NAME) and ``reversible`` are READ FROM
    the declared :class:`~dazzle_lib.states.Transition`, not hardcoded per verb.
    ``entity_identity`` is the carried identity of the entity the transition
    moved (a domain-neutral string; the consumer's ``identity_of`` hook supplies
    it). ``payload`` carries any axis-specific extra (e.g. a visibility ladder's
    channel deltas) until the per-axis receipts fully dissolve."""

    entity_identity: str
    axis: str
    previous_state: Any
    new_state: Any
    conserved: str
    reversible: bool
    verb: str
    payload: Any = None


@runtime_checkable
class VerbContext(Protocol):
    """The capability-side bedrock contract: a verb context can ``apply`` a verb
    to an (opaque) entity against a target and ``undo`` the resulting receipt.

    This is the thing that ADHERES to the bedrock for behavior -- a consumer's
    transition context, named so "bedrock declares, consumer adheres" is true of
    the capability, not just the value/identity contracts. Domain-neutral by
    design: the entity is ``Any`` (entity-opacity is the lift's whole point --
    the executor extracts nothing structural from the entity), and the verb
    vocabulary stays in the consumer. :class:`TransitionContext` is the bedrock's
    own reference implementation of this contract."""

    def apply(self, entity: Any, target: Any, *, verb: str) -> Receipt: ...
    def undo(self, receipt: Receipt) -> Receipt: ...


class TransitionContext:
    """One generic executor for any state axis.

    The shared apply/undo/criticality/receipt logic lives here ONCE; the per-axis
    substrate I/O + policy are consumer-supplied hooks bound to a handle:

    - ``detect(entity) -> current_value`` -- read the axis value off the substrate.
    - ``write(entity, target, prev) -> payload`` -- persist the move; return any
      axis-specific receipt payload (or ``None``).
    - ``identity_of(entity) -> str`` -- the entity's identity for the receipt /
      messages (a domain-neutral string; dazzlecmd supplies its FQCN). This is the
      seam that keeps the executor free of any one consumer's entity shape.
    - ``check(entity, target, verb, prev)`` -- OPTIONAL axis pre-flight (direction
      guards, target validity, a constitutional refusal); raises to refuse.
    - ``invert(receipt) -> (target, verb)`` -- OPTIONAL inverse move for ``undo``
      (defaults to re-applying ``previous_state`` with the same verb).

    ``apply`` resolves the declared edge for ``(verb, axis)`` so the receipt's
    ``conserved``/``reversible`` come from the registry, and refuses a
    ``REFUSED_AT_BOUNDARY`` edge generically. The substrate hooks keep the
    declared registry import-pure -- they declare the axis; the handle reads/writes.
    """

    def __init__(self, registry, axis_name, *, detect, write, identity_of,
                 check=None, invert=None):
        self._registry = registry
        self._axis_name = axis_name
        self._detect = detect
        self._write = write
        self._identity_of = identity_of
        self._check = check
        self._invert = invert
        self._applied_entity = None

    def _edge(self, verb):
        edges = [t for t in self._registry.for_verb(verb) if t.axis == self._axis_name]
        if not edges:
            raise LookupError(
                f"no declared transition for verb {verb!r} on axis {self._axis_name!r}"
            )
        return edges[0]

    def current(self, entity):
        """The entity's current value on this axis (via the detect hook)."""
        return self._detect(entity)

    def apply(self, entity, target, *, verb):
        prev = self._detect(entity)
        if self._check is not None:
            self._check(entity, target, verb, prev)
        edge = self._edge(verb)
        if edge.reversibility is Reversibility.REFUSED_AT_BOUNDARY:
            raise CriticalityBoundaryError(
                f"{self._identity_of(entity)}: {verb} on {self._axis_name} is refused "
                f"at the criticality boundary ({edge.conserved} cannot be preserved)"
            )
        payload = self._write(entity, target, prev)
        self._applied_entity = entity
        return Receipt(
            entity_identity=self._identity_of(entity),
            axis=self._axis_name,
            previous_state=prev,
            new_state=target,
            conserved=edge.conserved,
            reversible=edge.reversible,
            verb=verb,
            payload=payload,
        )

    def undo(self, receipt):
        if self._applied_entity is None:
            raise TransitionError(
                "TransitionContext.undo() requires a prior apply() on this context."
            )
        if self._invert is not None:
            target, verb = self._invert(receipt)
        else:
            target, verb = receipt.previous_state, receipt.verb
        return self.apply(self._applied_entity, target, verb=verb)


__all__ = [
    "CriticalityBoundaryError",
    "TransitionError",
    "Receipt",
    "VerbContext",
    "TransitionContext",
]
