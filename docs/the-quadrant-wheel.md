# The quadrant wheel: `QuadrantView` and the geometry behind it

This documents `QuadrantView` -- the shipped, pure, derived projection that models the **Scarcity Hypothesis (SH) four-quadrant cycle** over any two axes of a `ContinuumSpace` -- and, separately and clearly labelled, the SH-framework *geometry* it projects (the polar/quadrant picture that motivates it).

> **Read this banner first.** Two registers live in this doc and must not blur:
> - **LIBRARY (shipped, an API you call):** `QuadrantView` and its methods. Pure, derived from declared data, no effects.
> - **FRAMEWORK (a mental model / motivating source, NOT an API):** the polar `(r, θ)` picture, the trigonometric reading, and the `√−1`/τ generative rotation. The library does **not** store polar coordinates and exposes **no** trig API. Where this doc explains the geometry, it is teaching the *why*, not describing a callable surface. Every framework-only claim is marked **(framework)**.

## What is shipped vs. what is mental model

| Thing | Status | Note |
|---|---|---|
| `ContinuumSpace.quadrants(axis1, axis2) -> QuadrantView` | **shipped** | A pairwise *view* over two axes of an N-ary space -- never a structural 2-axis limit; `compose`/`normal_form` are unchanged. |
| `QuadrantView.{quadrants, hidden_at, agreement_diagonal, disagreement_diagonal, tau_steps}` | **shipped** | Pure lookups over the declared `_QUADRANT_SIG` / `_POLARITY_PHASES` / `_CHANNEL_PHASES` tables. |
| `Continuum` stored as polar `(r, θ)` | **(framework) -- evaluated and REJECTED** | `Continuum` stays a name-keyed signed-integer `ranks` axis. Polar was judged "structural rhyme, not load-bearing"; the reopen trigger is "a tool needs radian/θ at scale -> add it as a *derived view*, never as storage." Computing `(r, θ)` on demand is fine; storing it is not. |
| `√−1` / τ as a rotation that spawns an axis | **(framework)** | Generativity in the library is `Transition.kind {lateral \| generative \| refused}` (see [`states.py`](../dazzle_lib/states.py)). There is no `tau()`, no rotation, no complex number in the code. |
| Trig: `exigency=cos`, `good=sin`, `value=tan` | **(framework) only** | PDF-level framing with no code, constant, or API in the library. Cited here purely as the source picture. |

The one-line summary: **the SH cycle is natively a quadrant/polar wheel; the library models that wheel as `QuadrantView`, a pure derived projection, while the underlying `Continuum` remains a signed-integer axis.**

## The wheel (framework)

A `Continuum`, drawn as a signed line `cold (−) … 0 … warm (+)`, is the *real-axis projection* of a richer object. **(framework)** The fuller picture is a plane: the continuum is one axis, and its always-implicit **hidden orthogonal** (the imaginary / `i` axis -- the same "a Continuum implicitly carries a ContinuumSpace" relation from [the ladder](the-ladder.md), seen geometrically) is the other. The two signed axes partition the plane into four quadrants, which the SH framework reads as the four phases of a cycle:

| Quadrant | sign `(first, second)` | phase | figure / ground |
|---|---|---|---|
| **Q1** | `(+, +)` | **Peak** | visible (P) |
| **Q2** | `(−, +)` | **End** | visible (P) |
| **Q3** | `(−, −)` | **Hidden** | the **not-P** ground (renewal) |
| **Q4** | `(+, −)` | **Begin** | visible (P) |

The visible triad {Begin, Peak, End} is **P**; the fourth, **Hidden (Q3)**, is **not-P** -- "the visible triad completed by the hidden fourth that ensures renewal." Which framing you foreground -- the P triad or the Hidden ground -- is **directionality = Context**: the same axis read warm-first vs cold-first, two complete framings of one continuum (the `warm` / `cold` lenses on `Continuum` are the code embodiment of this choice; the additive/subtractive RGB↔CMYK duality is the same idea). Crossing into the not-P/Hidden frame is, **(framework)**, the generative move -- a π/2 rotation into the hidden orthogonal, the `√−1` step that spawns a new dimension. In the library that crossing is represented categorically, as a `generative` transition, not as a literal rotation.

## What the library ships: `QuadrantView`

`ContinuumSpace.quadrants(axis1, axis2)` returns a frozen `QuadrantView` -- a **pairwise projection** that picks two axes out of an N-ary space and reads the four-phase wheel over them. It is pure: every method is a lookup over declared sign/phase tables; it holds no state and changes nothing.

**Channel roles are a caller convention, not a constraint.** The view is channel-agnostic: you pass two axis names, and *by call order* you designate `axis1` as the first ("meaning") channel and `axis2` as the second ("position") channel. The library does not enforce which axis is which -- that designation is the consumer's.

The methods:

- **`quadrants() -> ((1,1), (−1,1), (−1,−1), (1,−1))`** -- the four `(first-sign, second-sign)` combos, in `Q1..Q4` order.
- **`hidden_at(quadrant) -> str`** -- which of the four *primitives* (`"+"`, `"−"`, `axis1`, or `axis2`) sits at its **Hidden** phase at that quadrant. This is the checkable criticality signal: the "absent primitive = hidden phase" recipe. Returns one of those four strings; raises on an unknown quadrant.
- **`agreement_diagonal() -> ("Q2", "Q4")`** and **`disagreement_diagonal() -> ("Q1", "Q3")`**. Read these carefully: *agreement* means the two channels **agree with each other** -- both at the same resolution status -- which is true at Q2 (both "same") *and* at Q4 (both "diff"); *disagreement* (Q1, Q3) is where one channel is resolved and the other is not. Agreement is **not** "both resolved."
- **`tau_steps() -> (axis, axis, axis, axis)`** -- walking the wheel `Q1→Q2→Q3→Q4→Q1`, exactly **one** channel flips at each boundary; this returns the axis name that flips at each step (the alternating L,M,L,M pattern). Note the name: a **"tau step" is this single-channel flip**, which is *not* the framework's broader "tau generative move" (the axis-spawning `√−1` operation). Same root word, different scope -- keep them distinct.

The phase names `"begin"`, `"peak"`, `"end"`, `"hidden"` are **string literals** in the library's declared `_POLARITY_PHASES` / `_CHANNEL_PHASES` tables (returned by `hidden_at`), not enum members or constants you import.

## Worked shape

Given a `ContinuumSpace` with (at least) two axes, `space.quadrants("meaning_axis", "position_axis")` lets a consumer ask "at the `Q3`/Hidden phase, which primitive is absent?" (`hidden_at("Q3")`) to detect the renewal/criticality point, or "which channel flips crossing `Q1→Q2`?" (`tau_steps()[0]`) to drive a phased traversal. Because it is a derived view, you can take as many pairwise wheels over an N-ary space as you have axis pairs -- the space itself is untouched.

## Out of scope (framework concepts with no library type)

So nobody hunts for these in the code:

- **Polar `(r, θ)` storage, the `√−1` rotation, and the trig functions** -- mental model only (see the table above). Compute `(r, θ)` on demand if a surface needs it; never store it.
- **SPCR** (Story/Puzzle/Content/Result, the framework's "how one continuum relates to the next") -- there is **no** `ContinuumSpace` relation layer for this; it is an identified gap, not an API.
- **The `(S, D, R)` transition triple and Scheme O/P/Π** -- PDF concepts that *motivate* `Transition.conserved` and the Receipt pattern; they are not named library types.

## See also

- [the-ladder.md](the-ladder.md) -- the base-object algebra (`Unified`/`Groupable`/`Continuum`/`ContinuumSpace`, aligned vs product, the signed invariant-bearing zero, fibers/channels). The "hidden orthogonal" this wheel makes geometric is the same one the ladder describes as a latent fiber.
- [`dazzle_lib/continuum.py`](../dazzle_lib/continuum.py) -- `QuadrantView`, and the `_QUADRANT_SIG` / `_POLARITY_PHASES` / `_CHANNEL_PHASES` tables that are its ground truth.
- [`dazzle_lib/states.py`](../dazzle_lib/states.py) -- `Transition` / `CompositeTransition` and `Transition.kind` (`lateral`/`generative`/`refused`): where generativity actually lives.
