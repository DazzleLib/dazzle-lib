# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to a PEP 440 versioning scheme (see `_version.py`).

Status: **beta**. The bedrock's surface is deliberately tiny and locked from day
one (`docs/api-stability.md`); changes land via the stack's shim policy
(temporary, noisy, tracked, terminal), never silently.

## [Unreleased]

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

[Unreleased]: https://github.com/DazzleLib/dazzle-lib/compare/v0.5.0...HEAD
[0.2.0]: https://github.com/DazzleLib/dazzle-lib/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/DazzleLib/dazzle-lib/releases/tag/v0.1.0
