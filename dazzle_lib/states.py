"""The generic state-system primitives -- axes, observed state, declared transitions.

These types give every grouping/ungrouping mechanism ONE vocabulary for the
states it moves between, the axes those states live on, which transitions are
reversible/critical, and what each transition preserves, creates, or destroys.
They are the L0 *machinery* of the state system; the DECLARED instances (which
axes a particular toolset has, which transitions are live) are the consumer's --
e.g. dazzlecmd's ``build_default_registry()`` registers the KIND/MODE/VISIBILITY/
ACTIVATION/ROUTING axes and the live ``rebind``/``hide``/``graduate`` edges.

Lifted to the dazzle-lib bedrock (B3b of dazzlecmd's Groupable<->Continuum<->
states unification; dazzle-lib 0.4.0). Until 0.4 these types lived in
``dazzlecmd_lib.states`` next to the dazzlecmd registry; the generic machinery
proved domain-neutral (it imports NOTHING from any aggregator -- axes are
*registered*, not hardcoded) and pure (stdlib + the ``Continuum`` primitive
only, no I/O), so it belongs in the foundation every ``dazzle-*`` tool composes
on. ``dazzlecmd_lib.states`` now re-exports these and keeps only its own
registry. The charter guard (``tests/test_charter.py``) pins the purity.

Design (the 2026-06-09 state-system DWP):

- **Generic by construction.** The core types import NOTHING from
  ``engine``/``mode``/``groupable`` -- axes are *registered*, not hardcoded, so
  the module ships in the standalone bedrock and any aggregator builds its own
  registry. The dependency direction is ``states`` <- groupable <- entity-verbs;
  the consumer's engine/mode register their axes.

- **State is OBSERVED, not stored** (F1). :class:`EntityState` is a frozen
  snapshot assembled on demand; the substrates (filesystem, config, the Python
  type, the index) stay authoritative. Only the entity's ``identity`` is carried
  by the entity itself -- a domain-neutral string (a consumer fills it with
  whatever names its entities; dazzlecmd uses its FQCN).

- **Transitions are DECLARED edges** (F2/F3). A :class:`Transition` names its
  axis, the states it goes from/to, its verb, its reversibility class, the
  conserved quantity (by NAME -- the context fills the runtime value, which keeps
  this module free of the consumer's invariant types), and the criticality
  bookkeeping (``creates``/``loses``/``identity_fate``). The
  :class:`TransitionRegistry` makes the criticality tables queryable.

- **The identity contract becomes a test** (F3.2). :func:`assert_round_trip`
  orchestrates read -> apply -> invert -> read and asserts L2-semantic equality
  (``group o ungroup = identity``, generated rather than asserted in prose). It
  is substrate-agnostic: ``read`` returns whatever observation the axis exposes,
  so the same harness covers both entity-axis and index-level transitions.

:class:`CompositeTransition` (multi-axis moves like graduation = KIND+MODE+
identity) is COMPOSITION of single-axis transitions, not a new primitive --
nothing in the single-axis types changes to accommodate it.

**PURE BY CHARTER.** This module imports ONLY stdlib typing/dataclasses/enum and
the sibling :mod:`dazzle_lib.continuum` primitive -- no ``os``/``subprocess``/
path/platform, no I/O, no effects. Effectful state changes (writing config, git,
filesystem) live in the *contexts* that CONSUME a registry, never here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping, Optional, Tuple

from .continuum import Continuum, ContinuumSpaceProtocol


# ---------------------------------------------------------------------------
# OPEN -- the sentinel for open-valued axes / wildcards
# ---------------------------------------------------------------------------
class _Open:
    """Sentinel: an open value space (e.g. ROUTING ranges over all FQCNs, not a
    fixed enum) or a wildcard in a transition's ``from_values``/``to_value``."""

    _instance: "Optional[_Open]" = None

    def __new__(cls) -> "_Open":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return "OPEN"


OPEN = _Open()


def _admits(allowed: Tuple[Any, ...], value: Any) -> bool:
    """True if ``value`` is in ``allowed`` or ``allowed`` wildcards via OPEN."""
    return any(a is OPEN or a == value for a in allowed)


# ---------------------------------------------------------------------------
# Reversibility -- the criticality algebra (the 5/2 bridge as data)
# ---------------------------------------------------------------------------
class Reversibility(Enum):
    """How a transition relates to its inverse -- straight from the corpus.

    - ``REVERSIBLE``: the inverse verb restores the prior state because the
      conserved invariant is preserved (in-orbit; ``receipt.reversible=True``).
    - ``ONE_WAY``: permitted, but it enters an orbit it cannot return from on its
      own (e.g. EMBEDDED -> publish -- a mini-graduation; ``reversible=False``).
    - ``REFUSED_AT_BOUNDARY``: the conserved invariant cannot be derived, so the
      transition would be irreversible -> refused PRE-FLIGHT
      (``CriticalityBoundaryError``).
    - ``GENERATIVE``: creates/destroys structure (ungroup / graduation);
      irreversible by construction -- ``creates``/``loses`` MUST be declared and
      ``identity_fate`` is typically ``"reborn"``.
    """

    REVERSIBLE = "reversible"
    ONE_WAY = "one_way"
    REFUSED_AT_BOUNDARY = "refused_at_boundary"
    GENERATIVE = "generative"


# ---------------------------------------------------------------------------
# StateAxis -- a named dimension an entity varies along
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class StateAxis:
    """One dimension of state, plus where its truth lives.

    ``values`` is the allowed value set, or ``None`` for an open-valued axis
    (ROUTING ranges over all FQCNs). When a ``continuum`` is supplied -- the
    signed, ordered backing (the unification's *StateAxis HAS-A Continuum* seam,
    B1) -- ``values`` DERIVES from it (single source: no ``values``/``ranks``
    drift); passing both that disagree is a contract breach, raised here.
    ``read_only`` marks an axis that the verbs do not transition directly (KIND
    -- changed only by graduation, a composite). ``detect`` is an optional reader
    hook into the substrate; it is intentionally left ``None`` in a default
    registry so this module imports nothing from a consumer's ``mode``/``engine``
    -- the axis documents its substrate, the consumer reads it.
    """

    name: str
    values: Optional[Tuple[Any, ...]] = None
    read_only: bool = False
    substrate: str = ""
    detect: Optional[Callable[..., Any]] = None
    continuum: Optional[Continuum] = None

    def __post_init__(self) -> None:
        # The HAS-A Continuum seam (B1): when an axis carries its signed/ordered
        # backing, the ordered value set IS the Continuum's -- derive it
        # (warm->cold) so there is ONE source, and refuse a ``values=`` that
        # disagrees rather than silently preferring one (the drift guard).
        if self.continuum is not None:
            if self.values is None:
                object.__setattr__(self, "values", self.continuum.levels()[::-1])
            elif set(self.values) != set(self.continuum.ranks):
                raise ValueError(
                    f"StateAxis {self.name!r}: values {tuple(self.values)!r} "
                    f"disagree with continuum {self.continuum.name!r} levels "
                    f"{tuple(self.continuum.ranks)!r} -- an axis has one value set"
                )

    def admits(self, value: Any) -> bool:
        """True if ``value`` is a legal value on this axis (open axes admit any)."""
        return self.values is None or value in self.values


# ---------------------------------------------------------------------------
# EntityState -- a frozen observation (NOT stored on the entity)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EntityState:
    """A measurement of an entity's state across one or more axes.

    Assembled on demand from the authoritative substrates and never persisted
    (F1). Carries the entity's ``identity`` (a domain-neutral string -- dazzlecmd
    fills it with the FQCN) plus an ``axis-name -> observed value`` mapping.
    Equality is by ``(identity, values)``; use :meth:`on` to compare a subset of
    axes (the L2-semantic round-trip check ignores axes a transition does not
    touch).
    """

    identity: str
    values: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Normalize to a plain dict copy (frozen => via object.__setattr__).
        object.__setattr__(self, "values", dict(self.values))

    def __getitem__(self, axis: str) -> Any:
        return self.values[axis]

    def get(self, axis: str, default: Any = None) -> Any:
        return self.values.get(axis, default)

    def on(self, *axes: str) -> "EntityState":
        """A restriction of this observation to ``axes`` (for subset equality)."""
        return EntityState(self.identity, {a: self.values[a] for a in axes if a in self.values})

    def coordinates_in(self, space: ContinuumSpaceProtocol) -> Mapping[str, int]:
        """This observation as a POINT in a :class:`ContinuumSpace` -- the signed
        presence coordinate for each of the space's axes that this state carries.

        The executable reading of "an ``EntityState`` is a point in the space"
        (the unification target): it pairs the OBSERVED value on each axis with
        the space's shared presence scale. Axes the state does not carry are
        skipped (a partial observation is a partial point); a carried value that
        is not a level of its axis surfaces as the Continuum's own error."""
        return {axis: space.presence_of(axis, self.values[axis])
                for axis in space.axes if axis in self.values}


# ---------------------------------------------------------------------------
# Transition -- a DECLARED edge on one axis
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Transition:
    """A declared, single-axis state-transition edge.

    ``conserved`` names the C2 invariant (e.g. ``"remote_url"``,
    ``"single_hop_rule"``); the runtime VALUE is supplied by the context's
    receipt, which is why this module declares the name only and never imports
    the consumer's invariant types. ``invariant_factory`` is a reserved hook for
    consumers that want the registry to build their descriptor type; it stays
    ``None`` in a default registry to preserve ``states <- groupable``.

    ``creates``/``loses``/``identity_fate`` make the criticality bridging points
    declared DATA: what a transition brings into being, what it destroys, and
    what becomes of the entity's identity (``"preserved"`` | ``"reborn"`` |
    ``"dissolved"``).
    """

    axis: str
    from_values: Tuple[Any, ...]
    to_value: Any
    verb: str
    reversibility: Reversibility
    conserved: str = ""
    invariant_factory: Optional[Callable[..., Any]] = None
    creates: Tuple[str, ...] = ()
    loses: Tuple[str, ...] = ()
    identity_fate: str = "preserved"
    note: str = ""

    def __post_init__(self) -> None:
        # A GENERATIVE edge must declare what it brings into being / destroys --
        # the criticality bridging points are not allowed to be implicit.
        if self.reversibility is Reversibility.GENERATIVE and not (self.creates or self.loses):
            raise ValueError(
                f"GENERATIVE transition ({self.verb} on {self.axis}) must declare "
                f"creates and/or loses -- the criticality must be explicit data."
            )
        # A REVERSIBLE edge must preserve identity (the carried invariant).
        if self.reversibility is Reversibility.REVERSIBLE and self.identity_fate != "preserved":
            raise ValueError(
                f"REVERSIBLE transition ({self.verb} on {self.axis}) must preserve "
                f"identity; got identity_fate={self.identity_fate!r}."
            )

    @property
    def reversible(self) -> bool:
        """Whether the inverse verb restores the prior state (REVERSIBLE only)."""
        return self.reversibility is Reversibility.REVERSIBLE

    @property
    def kind(self) -> str:
        """The SH-redesign vocabulary, DERIVED from ``reversibility`` (no duplicate
        field). Maps ALL FOUR reversibility classes -- only ``"lateral"``
        round-trips; the other three are the non-lateral (lossy / refused) classes:

        - ``REVERSIBLE  -> "lateral"``    -- a move WITHIN the space; round-trips.
        - ``ONE_WAY     -> "one-way"``    -- permitted but cannot return on its own
          (a mini-graduation, e.g. embedded->publish); lossy-on-reverse, NO
          structure created.
        - ``GENERATIVE  -> "generative"`` -- spawns/destroys structure (the sqrt(-1)
          move); lossy-on-reverse unless a ``Receipt`` preserves it (spike C13).
        - ``REFUSED_AT_BOUNDARY -> "refused"`` -- criticality refuses it pre-flight.

        Completeness is pinned by ``test_kind_covers_every_reversibility`` -- a new
        ``Reversibility`` value with no mapping fails the suite (no silent
        fallback)."""
        return {
            Reversibility.REVERSIBLE: "lateral",
            Reversibility.ONE_WAY: "one-way",
            Reversibility.GENERATIVE: "generative",
            Reversibility.REFUSED_AT_BOUNDARY: "refused",
        }[self.reversibility]

    def matches(self, *, verb: str, axis: str, from_value: Any, to_value: Any = OPEN) -> bool:
        """Whether this declared edge covers an observed ``(verb, axis, from -> to)``."""
        if verb != self.verb or axis != self.axis:
            return False
        if not _admits(self.from_values, from_value):
            return False
        if to_value is not OPEN and self.to_value is not OPEN and to_value != self.to_value:
            return False
        return True


# ---------------------------------------------------------------------------
# CompositeTransition -- a multi-axis move as ordered composition (graduation)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CompositeTransition:
    """A multi-axis transition: an ORDERED composition of single-axis legs.

    Graduation (tool -> own repo -> kit/aggregator) is the canonical case: it
    changes KIND + MODE + identity at once. This is COMPOSITION, not a new
    primitive -- the legs are ordinary :class:`Transition` objects; this
    aggregates them with an order (the legs are not freely commutable -- you
    cannot publish a submodule against a remote the extraction leg hasn't created
    yet) and an atomicity policy.

    The load-bearing rule -- **composite-criticality is NOT the union of the
    legs' classes.** If any leg's ``creates`` feeds a LATER leg's conserved
    invariant, the whole is GENERATIVE even when every leg, taken alone, is
    reversible (the 5/2 structural bridge at composite scale). Otherwise the
    composite is as strong as its strongest leg.
    """

    name: str
    legs: Tuple[Transition, ...]
    verb: str
    atomicity: str = "all_or_nothing"   # "all_or_nothing" | "checkpoint"
    identity_fate: str = "reborn"

    def __post_init__(self) -> None:
        if not self.legs:
            raise ValueError("CompositeTransition must declare at least one leg")

    @property
    def reversibility(self) -> Reversibility:
        # Interaction first: a leg that CREATES a quantity a later leg CONSERVES
        # crosses the criticality boundary -> generative (this is the case where
        # the composite is strictly stronger than the union of its legs).
        for i, leg in enumerate(self.legs):
            created = set(leg.creates)
            for later in self.legs[i + 1:]:
                if later.conserved and later.conserved in created:
                    return Reversibility.GENERATIVE
        # Otherwise: as strong as the strongest leg.
        classes = {leg.reversibility for leg in self.legs}
        for strongest in (Reversibility.GENERATIVE, Reversibility.REFUSED_AT_BOUNDARY,
                          Reversibility.ONE_WAY):
            if strongest in classes:
                return strongest
        return Reversibility.REVERSIBLE

    @property
    def creates(self) -> Tuple[str, ...]:
        return tuple(c for leg in self.legs for c in leg.creates)

    @property
    def loses(self) -> Tuple[str, ...]:
        return tuple(x for leg in self.legs for x in leg.loses)

    @property
    def axes(self) -> Tuple[str, ...]:
        return tuple(leg.axis for leg in self.legs)


# ---------------------------------------------------------------------------
# TransitionRegistry -- the criticality tables, queryable
# ---------------------------------------------------------------------------
class TransitionRegistry:
    """A catalogue of registered axes and declared transitions.

    Powers receipt truthfulness (contexts look up the declared reversibility /
    invariant instead of hardcoding it), the round-trip harness (property tests
    enumerate the edges), and explainability.
    """

    def __init__(self) -> None:
        self._axes: dict[str, StateAxis] = {}
        self._transitions: list[Transition] = []
        self._composites: list[CompositeTransition] = []

    # -- axes -----------------------------------------------------------------
    def register_axis(self, axis: StateAxis) -> StateAxis:
        if axis.name in self._axes:
            raise ValueError(f"axis {axis.name!r} is already registered")
        self._axes[axis.name] = axis
        return axis

    def axis(self, name: str) -> StateAxis:
        return self._axes[name]

    def axes(self) -> Tuple[StateAxis, ...]:
        return tuple(self._axes.values())

    # -- transitions ----------------------------------------------------------
    def declare(self, transition: Transition) -> Transition:
        """Register a transition, validating its endpoints against its axis."""
        axis = self._axes.get(transition.axis)
        if axis is None:
            raise KeyError(
                f"transition references unregistered axis {transition.axis!r}; "
                f"register the axis first"
            )
        for fv in transition.from_values:
            if fv is not OPEN and not axis.admits(fv):
                raise ValueError(
                    f"transition from_value {fv!r} not admitted by axis "
                    f"{axis.name!r} (values={axis.values!r})"
                )
        if transition.to_value is not OPEN and not axis.admits(transition.to_value):
            raise ValueError(
                f"transition to_value {transition.to_value!r} not admitted by axis "
                f"{axis.name!r} (values={axis.values!r})"
            )
        self._transitions.append(transition)
        return transition

    def transitions(self) -> Tuple[Transition, ...]:
        return tuple(self._transitions)

    # -- composites (multi-axis) ---------------------------------------------
    def register_composite(self, composite: CompositeTransition) -> CompositeTransition:
        """Register a multi-axis composite; validate each leg's axis is known."""
        for leg in composite.legs:
            if leg.axis not in self._axes:
                raise KeyError(
                    f"composite {composite.name!r} leg references unregistered "
                    f"axis {leg.axis!r}"
                )
        self._composites.append(composite)
        return composite

    def composites(self) -> Tuple[CompositeTransition, ...]:
        return tuple(self._composites)

    def composite(self, name: str) -> CompositeTransition:
        for c in self._composites:
            if c.name == name:
                return c
        raise LookupError(f"no composite transition named {name!r}")

    def for_verb(self, verb: str) -> Tuple[Transition, ...]:
        return tuple(t for t in self._transitions if t.verb == verb)

    def for_axis(self, axis: str) -> Tuple[Transition, ...]:
        return tuple(t for t in self._transitions if t.axis == axis)

    def by_reversibility(self, reversibility: Reversibility) -> Tuple[Transition, ...]:
        return tuple(t for t in self._transitions if t.reversibility is reversibility)

    def find(self, *, verb: str, axis: str, from_value: Any, to_value: Any = OPEN) -> Optional[Transition]:
        """The declared edge covering ``(verb, axis, from -> to)``, or ``None``."""
        for t in self._transitions:
            if t.matches(verb=verb, axis=axis, from_value=from_value, to_value=to_value):
                return t
        return None

    def lookup(self, *, verb: str, axis: str, from_value: Any, to_value: Any = OPEN) -> Transition:
        """Like :meth:`find` but raises ``LookupError`` if no edge matches."""
        t = self.find(verb=verb, axis=axis, from_value=from_value, to_value=to_value)
        if t is None:
            raise LookupError(
                f"no declared transition for verb={verb!r} axis={axis!r} "
                f"from={from_value!r} to={to_value!r}"
            )
        return t


# ---------------------------------------------------------------------------
# assert_round_trip -- the identity contract as an executable check
# ---------------------------------------------------------------------------
class _Unset:
    pass


_UNSET = _Unset()


def assert_round_trip(
    read: Callable[[], Any],
    apply: Callable[[], Any],
    invert: Callable[[Any], Any],
    *,
    expected_new: Any = _UNSET,
) -> Any:
    """Assert ``apply`` then ``invert`` restores the observed state (L2-semantic).

    Substrate-agnostic by design: ``read`` returns whatever observation the axis
    exposes (a MODE state value, an alias's current target), ``apply`` performs
    the transition and returns its receipt, and ``invert`` consumes that receipt
    to walk the edge back. The equality is on whatever ``read`` returns, so the
    same harness covers entity-axis and index-level (routing) transitions. When
    ``invert`` re-applies the verb toward ``receipt.previous_state`` the verb is
    its own inverse; once a context exposes ``ctx.undo(receipt)`` it becomes
    ``invert=ctx.undo`` with no change here.

    Returns the receipt from ``apply`` so callers can assert on it.
    """
    before = read()
    receipt = apply()
    if expected_new is not _UNSET:
        observed_new = read()
        if observed_new != expected_new:
            raise AssertionError(
                f"transition did not reach the expected state: "
                f"expected {expected_new!r}, observed {observed_new!r}"
            )
    invert(receipt)
    restored = read()
    if restored != before:
        raise AssertionError(
            f"round-trip is not the identity (L2): before={before!r} "
            f"restored={restored!r}"
        )
    return receipt


# ---------------------------------------------------------------------------
# observe -- assemble a VALIDATED EntityState from platform readings
# ---------------------------------------------------------------------------
def observe(registry: TransitionRegistry, identity: str, **axis_values: Any) -> EntityState:
    """Build an :class:`EntityState` from per-axis readings, validated against
    the registered axes.

    The bridge between the platform and the model: the *consumer* reads its own
    substrates and passes the readings here; this function asserts each reading
    is something the model can express. A value an axis does not admit is a
    contract breach -- either the model is missing a value or the reading is
    wrong -- and is raised rather than silently stored. Stays generic: no
    substrate access happens here, so this module still imports nothing from a
    consumer's ``engine``/``mode``.
    """
    for name, value in axis_values.items():
        try:
            axis = registry.axis(name)
        except KeyError:
            raise KeyError(f"observed unknown axis {name!r} (not registered)") from None
        if not axis.admits(value):
            raise ValueError(
                f"observed value {value!r} on axis {name!r} is not admitted by the "
                f"state model (axis values={axis.values!r}); the model does not "
                f"cover this platform state"
            )
    return EntityState(identity, dict(axis_values))


__all__ = [
    "OPEN",
    "Reversibility",
    "StateAxis",
    "EntityState",
    "Transition",
    "CompositeTransition",
    "TransitionRegistry",
    "assert_round_trip",
    "observe",
]
