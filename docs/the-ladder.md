# The ladder: `Unified` -> `Groupable` -> `Continuum` -> `ContinuumSpace`

The conceptual model behind `dazzle_lib.groupable` + `dazzle_lib.continuum`. Read this once and the base objects stop being four unrelated classes and become one idea viewed at four scales. It is the answer to "why is a `Continuum` not just an enum?" and "what is the difference between `compose` and a fiber?"

Everything here is **pure** (stdlib-only, side-effect-free, by charter -- see the README). The ladder is computation over data; the effects that *consume* it (writing config, git, the filesystem) live in the consumer's contexts, never in these objects.

## The four ladder types

| Type | What it is | Carries (implicitly) |
|---|---|---|
| `Unified` | A single label *before the cut* -- a concept named as one thing (the SH `0_ag`). | a `Groupable` (`.groupable()` performs the cut) |
| `Groupable` | The `{minus, plus}` dual sharing one `meaning` -- the two poles an axis is the unification of. Every Groupable `.invert()`s; there is no one-way value. | a `Continuum` (the degenerate, 2-level case) |
| `Continuum` | A signed, totally-ordered axis with an **invariant-bearing zero**: `cold (-N) ... 0 (neutral) ... warm (+M)`. | a `ContinuumSpace` (every rung can host an orthogonal sub-structure) |
| `ContinuumSpace` | A composition of N `Continuum` axes -- either fused onto one shared scale (*aligned*) or multiplied (*product*). | (recurses: an axis may itself be a `ContinuumSpace`) |

The "carries implicitly" column is the spine of the whole design. From `Unified`'s docstring, verbatim:

> *Just as a Continuum implicitly carries a ContinuumSpace, a unified value implicitly carries its Groupable.*

Each level is the next level not-yet-unfolded. You climb the ladder by **unfolding** (a `Unified` cuts into a `Groupable`; a `Groupable` refines into a `Continuum`; a `Continuum`'s rung grows an orthogonal `ContinuumSpace`) and descend it by **collapsing**. One operation -- grouping / ungrouping -- at every rung.

## Axis is the same thing as continuum

A recurring source of confusion: "is this an *axis* or a *continuum*?" They are **the same structure**, named for the role it is playing:

- **continuum** = the structure viewed *intrinsically* (the ordered, signed chain);
- **axis** = that same continuum serving as a *coordinate / direction* of a space.

So "all continua are axes" simply means "any ordered chain can serve as a coordinate." There is no continuum that is not an axis and no axis that is not a continuum. The question that *does* carry information is never "axis or continuum?" -- it is **"is this composition *aligned* or a *product*?"** (below).

## The signed, invariant-bearing zero

A `Continuum`'s `0` is **not** "nothing" and **not** an endpoint. It is the neutral, no-lean state where the conserved `invariant` is purely held; the two halves are departures from it:

- `> 0` (**warm**) -- *more* of the quality is expressed (enrichment: add a plugin, raise verbosity, become more visible);
- `< 0` (**cold**) -- *less* is expressed (letting-go: disable, hide, unload);
- the **poles** (`-N`, `+M`) are the **criticality boundaries** where the invariant breaks. The continuum itself refuses to step past a pole (`ContinuumBoundaryError`); whether a pole-*crossing* operation (remove, graduate) is allowed is the consuming context's decision, not the primitive's.

This is the THAC0 logger model (`NOTHING=-4 ... DEFAULT=0 ... DEBUG=+3`, gate `level <= threshold`) generalized so the *same* primitive serves a visibility ladder, an activation toggle, a load/pointer spectrum, and log verbosity.

## Two directions of structure: axes (outward) and fibers (inward)

A `Continuum` is *not* a flat chain. Every rung can host more structure, in two orthogonal directions:

- **OUTWARD** -- `ContinuumSpace.axes`: compose this continuum *alongside* others into a space. This is `compose()` / `normal_form()`.
- **INWARD** -- `Continuum.fibers`: hang a sub-structure *over a single rung's position*. A fiber is any ladder element: `RungValue = Unified | Groupable | Continuum | ContinuumSpace`. (`Continuum.channels` is a second, simpler inward dimension: the monotone channel set a rung suppresses/activates -- e.g. a log level's per-channel thresholds, a visibility level's hint/display/resolution surfaces.)

Both directions are children. `children(node)` is **total** over the four ladder types -- a `ContinuumSpace` yields its axes (outward), a `Continuum` yields its fibers (inward), a `Groupable`/`Unified` is a leaf -- and `walk()` / `fold()` traverse axes and fibers **uniformly** ("direction is not special"). One pure recursion serializes, folds, or visits the entire structure.

### Latent by design: the contract is typed, the storage is lazy

A bare `Continuum` ships with `fibers = {}`. The orthogonal sub-structure is **first-class but unmaterialized** -- the slot and its `RungValue` type exist; the value is filled only when a consumer needs it. This is deliberate, not unfinished: **eager** materialization would infinite-regress (every rung's fiber is itself a continuum with rungs that have fibers, forever). So "every continuum implicitly carries a space" is a *latent* truth -- realized on demand, paid for only where used. An un-fibered continuum is byte-identical to one that never heard of fibers.

> The *geometry* of this hidden orthogonal -- the four-quadrant wheel two axes sweep, and the `QuadrantView` that projects it -- is [the-quadrant-wheel.md](the-quadrant-wheel.md). (The polar `(r, θ)` picture there is a mental model; the library stores signed-int ranks, not coordinates.)

## `ContinuumSpace`: aligned (fusion) vs product (multiplication)

A `ContinuumSpace` composes N continua. The single most important property is its **coupling**, set at construction by whether `presence` is supplied:

### Aligned -- a 2D fusion (NOT a 1D collapse)

When `presence` is given, the axes are threaded onto **one shared, strictly-ordered merged scale** (the *spectrum*). Crucially, this **retains** every constituent: `axes` still holds each `Continuum` (its own mechanism) *and* `presence` adds the common order. So an aligned space is inherently **2D** -- a foregrounded common axis *plus* the retained per-constituent axes -- never a flattening of N axes into one.

Because there is one merged order, cross-axis navigation works: `colder_than` / `warmer_than` can hop from one axis's cold rung to another's, `spectrum()` is the navigable ladder, `cascade_to_neutral` / `slice` move bands of rungs at once.

> Example consumer (dazzlecmd's kit lifecycle): a kit's `{activation, loading, materialization, membership}` continua are **fused** onto one common `{kit}` axis -- `active(0) > disabled(-1) > detached(-2) > pointer(-3) > gone(-4)` -- because they are nested (to be active a kit must be loaded; to be loaded, materialized; to be materialized, a member). Each remains its own axis; the common scale is the foreground.

### Product -- a literal multiplication

When `presence is None`, the axes are **independent dimensions on their own scales** -- a literal product, with the in-between points a product implies and **no** merged spectrum. Cross-axis navigation is **undefined by design** (`_require_aligned` raises) -- this is scale-safety, not a missing feature: "one axis's cold" and "another's cold" are not comparable, so the space refuses to pretend they are. `compose()` builds product spaces; `normal_form()` folds nested products to the flat leaf product (a product of products is a product -- the composition is closed).

> Example consumer: a visibility group whose `silence` / `hide` / `shadow` channels are *independent* (you can silence without hiding) is a product -- cascading across them is an explicit, opt-in choice, not an intrinsic order.

### The test for which one you have

Walk from an extremum toward `0` and ask whether the cascade **makes sense at every rung**. If yes -- each intermediate is a valid state and the order is monotone -- the composition is genuinely *aligned* (build it with a `presence` spectrum). If some columns stay independent (a rung you'd want to leave set regardless of its neighbors), it is a *product* (compose it, navigate per-leaf, cascade only on explicit request). Aligning a product would invent a false order; producting an alignment would forfeit real navigation.

## Why this shape (the one-paragraph rationale)

The stack needs ordered, reversible, *composable* state ladders that mean the same thing in a logger, a visibility surface, a kit lifecycle, and a wet/dry sensor -- without each consumer reinventing ordering, poles, reversibility, and cascade. Modeling them as **one recursive ladder** (`Unified`/`Groupable`/`Continuum`/`ContinuumSpace`, each implicitly carrying the next, closed under composition) means a single pure vocabulary covers all of them, the `{group, ungroup}` operation is the same at every scale, and a consumer only has to *declare* its axes and edges -- the criticality algebra, navigation, and serialization come for free. The objects stay dumb and pure; the consumer's contexts hold the effects.

## See also

- [the-quadrant-wheel.md](the-quadrant-wheel.md) -- the four-phase SH wheel: `QuadrantView` (shipped) and the polar/quadrant geometry it projects (mental model). The geometric face of the hidden orthogonal above.
- [`dazzle_lib/groupable.py`](../dazzle_lib/groupable.py) -- `Unified`, `Groupable`.
- [`dazzle_lib/continuum.py`](../dazzle_lib/continuum.py) -- `Continuum`, `ContinuumSpace`, `RungValue`, `children` / `walk` / `fold`.
- [`dazzle_lib/states.py`](../dazzle_lib/states.py) -- `StateAxis`, `EntityState`, `Transition` / `CompositeTransition`, `TransitionRegistry`: the state-system machinery a consumer declares its axes and edges in (a point in a `ContinuumSpace`; reversible / generative edges; `assert_round_trip`).
- [`api-stability.md`](api-stability.md) -- what is frozen vs evolving.
