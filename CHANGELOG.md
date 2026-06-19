# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to a PEP 440 versioning scheme (see `_version.py`).

Status: **beta**. The bedrock's surface is deliberately tiny and locked from day
one (`docs/api-stability.md`); changes land via the stack's shim policy
(temporary, noisy, tracked, terminal), never silently.

## [Unreleased]

## [0.6.2] -- 2026-06-19

### Added
- **The ladder bridges on `Continuum` (SH-grounded base-object redesign, Step 2): `poles()`, `densify_between()`, `Continuum.from_groupable()`, and the `RungValue` alias.** `poles()` returns the axis's bounds as a `Groupable` (cold pole = `minus`, warm pole = `plus`) -- a Groupable IS what a Continuum's bounds are (the always-present extrema role). `densify_between(lower, upper, new_level)` inserts a new NAMED rung at the exact MEDIANT `Fraction` strictly between two existing rungs (group/ungroup at the axis level; ports spike C2) -- existing int rungs are untouched, so an un-densified continuum stays byte-identical. `Continuum.from_groupable(g)` materializes a Groupable's implicit degenerate continuum `{minus:-1, plus:+1}` (the `Unified -> Groupable -> Continuum` bridge; lives on `Continuum` to keep bedrock layering acyclic). `RungValue = Unified | Groupable | Continuum | ContinuumSpace` names the per-rung-fiber contract (spike C12); fiber STORAGE on `Continuum` is deferred until a consumer needs it. Purely method-additive -- no dataclass shape change, no consumer churn; claims port spike C1/C2 (`test_continuum_bridges.py`). The production `Continuum` stays NAME-keyed (correcting the signoff DWP's position-keyed `rungs`); see the Step-2 DWP.

## [0.6.1] -- 2026-06-19

### Added
- **The ladder floor (`dazzle_lib.groupable`): `Groupable` (the `{minus, plus}` dual that is the BOUNDS of an axis) + `Unified` (the 0_ag pre-cut form that is IMPLICITLY a Groupable).** The bottom two rungs of the recursive ladder `Unified -> Groupable -> Continuum -> ContinuumSpace`. `Groupable.invert()` swaps the poles (every value is a dual -- invertibility is the FLOOR, nothing is one-way); `Groupable.unified(label)` builds the cheap one-label form with a *derived* inverse; `Unified.groupable()` performs the cut. Pure + import-clean by charter (stdlib only; `test_charter` green with the module present). The first slice of the SH-grounded base-object redesign; the `densify()`/`poles()` bridges to `Continuum` land with the Continuum rework (they would couple the modules). Grounded in D. Darcy's SH-Mechanics ("an axis is the unification of its two poles"); the claims port spike C1/C11 (`test_groupable.py`).

## [0.6.0] -- 2026-06-18

### Changed
- **`ContinuumSpace` is now CLOSED under composition -- the functionally-complete composition algebra.** A dimension may be a `Continuum` OR a `ContinuumSpace` (recursive), so `ContinuumSpace.compose(name, members)` yields a `ContinuumSpace` (closure: a product of products is a product) and `normal_form()` FOLDS arbitrary nesting back to a flat product over the leaf Continuums (qualified dotted names; idempotent + associative). `{Continuum, ContinuumSpace, compose}` is complete the way `{+, x, ^}` is -- the third construct folds back into itself (`3^3^3 -> 3^27`), so arbitrary dimensions need only these three; no level-4 type.
- **Alignment is now a PROPERTY, not a requirement.** The single merged presence spectrum (the prior hard contract) applies to an *aligned* space (`presence=` given -> all axes must be Continuums; validated exactly as before -- backward-compatible). A `compose`d **product** space (`presence=None`) holds independent, differently-scaled dimensions and refuses cross-axis navigation (`spectrum`/`colder_than`/`warmer_than`/`presence_of`/`cascade_to_neutral` raise `ContinuumError`) BY DESIGN -- scale-safety (you cannot compare "how visible" to "which mode"). `is_aligned` reports which a space is.
- **Why now:** validated experiment-first by representing the arithmetic operation hierarchy in the system (the spike: `+/-`,`x/div` = degenerate/commutative continuums = "Groupables"; `^/log/root` = the full non-commutative continuum with two inverses; `group` = compression between levels). The current hard-aligned space could NOT hold the three differently-scaled levels -- proving the generalization necessary, not assumed. No existing behavior changed (62 tests; the aligned path + `KIT_PRESENCE_SPACE` are byte-identical). `tests/test_continuum_composition.py` gates the closure laws.

## [0.5.0] -- 2026-06-17

### Added
- **The generic transition executor (`dazzle_lib.transitions`)** -- `TransitionContext` (one engine that runs any declared state axis: read current value, resolve the declared edge so the receipt's `conserved`/`reversible` come from the registry, refuse a `REFUSED_AT_BOUNDARY` edge, write the substrate, return a `Receipt`; `undo` round-trips), `Receipt` (the generic record one transition leaves -- the collapse of the per-verb `*Receipt` types), and the typed failures `CriticalityBoundaryError` (pre-flight refusal) / `TransitionError` (apply/undo failure). Exported from the package root.
- The executor is generic over an INJECTED registry + consumer-supplied hooks (`detect`/`write`/`identity_of`/`check`/`invert`); the per-verb contexts that bind real substrates (alias rebind, mode switch, visibility, containment, projection) stay in the consumer. Charter-safe: stdlib + `dazzle_lib.states` (`Reversibility`) only, no I/O. Lifted from `dazzlecmd_lib.groupable` (B3c of dazzlecmd's Groupable<->Continuum<->states unification).
- **Identity enters through a hook, not an attribute.** The executor's one coupling to a consumer was an `entity.fqcn` access; it is now an `identity_of(entity) -> str` hook (the same shape as the `detect`/`write` hooks), and `Receipt.entity_identity` is a domain-neutral string. The engine assumes nothing about the entity's type -- a consumer with no FQCN can use it (the smoke tests drive it with an entity that has no `.fqcn`).

### Changed
- Unlike the 0.3/0.4 lifts (verbatim), the executor was lifted WITH a generalization -- the `identity_of` seam replaces the hardcoded `entity.fqcn`. Behavior-equivalence is proven by the suite, not by AST-identity. No guarantee weakened.

## [0.4.0] -- 2026-06-17

### Added
- **The generic state-system primitives (`dazzle_lib.states`)** -- `StateAxis` (a named dimension; HAS-A optional `Continuum` backing that derives its ordered value set), `EntityState` (a frozen, OBSERVED-not-stored snapshot; `coordinates_in` reads it as a point in a `ContinuumSpace`), `Transition` (a declared single-axis edge carrying its `Reversibility` class + the conserved-invariant NAME + criticality data), `CompositeTransition` (a multi-axis move as ordered composition -- criticality is the leg-interaction result, NOT the union of leg classes), `TransitionRegistry` (the criticality tables made queryable), plus `assert_round_trip` (the `group o ungroup = identity` contract as a substrate-agnostic executable check) and `observe` (validated state assembly). Exported from the package root.
- These are the L0 *machinery* of the state system; the DECLARED instances (which axes a toolset has, which transitions are live) stay in the consumer -- so the bedrock ships the vocabulary and each aggregator builds its own registry. Charter-safe: stdlib + the sibling `Continuum` primitive only, no I/O, no effects (`tests/test_charter.py` green with the module present). Lifted from `dazzlecmd_lib.states` (B3b of dazzlecmd's Groupable<->Continuum<->states unification); that module now re-exports these and keeps only its own registry.
- **Domain-neutral identity vocabulary.** `EntityState.identity` / `Transition.identity_fate` (and `observe(registry, identity, ...)`) carry a generic identity string -- NOT the aggregator FQCN concept the original dazzlecmd code named them after. A consumer fills `identity` with whatever names its entities (dazzlecmd maps its FQCN onto it); a non-aggregator dazzle-* tool is free to use the state system without an FQCN. The bedrock stays neutral by charter; the dazzlecmd-flavored names (`fqcn`/`fqcn_fate`, the constitutional `C1` label) were neutralized at the lift before any consumer shipped.

### Changed
- Charter status note: the 0.3 "types + pure primitives" charter now holds its second primitive group. No guarantee weakened -- the state types are pure data + pure functions over declared edges; effectful transitions live in the *contexts* that consume a registry, never here.

## [0.3.0] -- 2026-06-17

### Changed
- **Charter evolved: "types only" -> "types + pure primitives".** The bedrock now holds pure, stdlib-only computational PRIMITIVES alongside the Protocols / TypedDict schemas / exception root. The hard guarantees are UNCHANGED -- still stdlib-only, still side-effect-free (no I/O, path handling, platform probing, or subprocess); `tests/test_charter.py` still enforces them (with `__future__` allowlisted as a PEP-563 compiler directive, not a behavior import). **Why:** the dazzle-* stack needs shared *composable* primitives, not only contract types -- so tools compose on one implementation instead of re-deriving it. The first primitive was proven in dazzlecmd's Groupable<->Continuum<->states unification and pulled into the bedrock here.

### Added
- **`Continuum` + `ContinuumSpace` (`dazzle_lib.continuum`)** -- the signed ordered-axis primitive (totally-ordered signed ranks with an invariant-bearing zero; `step`/`passes` THAC0 gate; warm/cold lens; optional channel backing) and the N-axis presence composition (`slice`, `cascade_to_neutral`, `colder_than`/`warmer_than`, `spectrum`, `describe`). `ContinuumProtocol` / `ContinuumSpaceProtocol` are the structural contracts (`runtime_checkable`). Exported from the package root.

## [0.2.0] -- 2026-06-17

### Added
- **`PathVariantResolver`** (`dazzle_lib.protocols`): a structural
  `runtime_checkable` Protocol that proposes alternative names for a path (e.g.
  a Windows UNC path and its mapped-drive equivalent) so a consumer can retry a
  failed operation under another name. It is the bedrock half of the stack's
  `path_variant_resolver` seam (STACK-MAP D7) and satisfies the rule of two:
  `dazzle-filekit` consumes it (UNC<->mapped fallback I/O), `unctools` is the
  canonical resolver. `str` in / `Sequence[str]` out -- pathlib stays out of the
  bedrock. Locked in `docs/api-stability.md`; charter test still green. 21 tests.

## [0.1.0] -- 2026-06-11

Initial release: Phase F of the DazzleLib stack plan
([architecture contract](https://github.com/DazzleLib/.github/blob/main/docs/STACK-MAP.md),
epic [DazzleLib/.github#3](https://github.com/DazzleLib/.github/issues/3)).

### Added
- **Protocols** (`dazzle_lib.protocols`): `Viewable` (`summary()`/`__str__`) and
  `Serializable` (`to_dict`/`from_dict`/`to_json`, `SCHEMA_VERSION`) -- structural,
  `runtime_checkable`, no subclassing required.
- **Payload schemas** (`dazzle_lib.payloads`): `FileMetadataDict`,
  `TimestampsDict`, `WindowsMetadataDict`, `UnixMetadataDict`, `LinkTargetDict`,
  `HashResultDict` -- the cross-layer TypedDict shapes, mirroring what
  `dazzle-filekit` actually produces (typing change, not behavior change).
- **Exception bedrock** (`dazzle_lib.exceptions`): `DazzleError` root +
  `PathIdentityError` / `FileOperationError` / `LinkError` / `PreserveError`
  domain bases.
- **`DazzleDataMixin`** (`dazzle_lib.mixins`): derives `to_json`/`summary`/
  `__str__` from a host class's `to_dict`.
- **Day-one guards**: `docs/api-stability.md` + import-stability canary, and the
  **charter test** (`tests/test_charter.py`) -- fails on any behavior-bearing or
  non-stdlib import in the package, red-green verified. 19 tests.

### Notes
- MIT, stdlib-only, Python >=3.9, no entry points -- a pure library by design.

[Unreleased]: https://github.com/DazzleLib/dazzle-lib/compare/v0.6.2...HEAD
[0.2.0]: https://github.com/DazzleLib/dazzle-lib/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/DazzleLib/dazzle-lib/releases/tag/v0.1.0
