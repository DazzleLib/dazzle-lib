"""Additional seam beyond the two pinned tripwires (dazzlecmd-lib 69126b4,
`tests/test_fqcn_tree.py::TestNumericAddressingGaps`) for the numeric
address system's ANONYMOUS-rung gap.

Those two tripwires pin: (1) a NON-INTEGER fraction anon rung ("5/2") is
unaddressable through the FQCN grammar/tree, and (2) custom mounts outside
FIBER_ROOTS forgive away. Both are grammar/canonicalization seams.

THIS is a third, distinct seam: SERIALIZATION. `densify_between` ALWAYS
promotes the new anon rung's rank to a `fractions.Fraction` -- even when
the mediant is a whole number (e.g. densifying between -1 and 1 gives an
anon "0" whose stored rank is `Fraction(0, 1)`, not the plain `int` 0 that
every OTHER rung in the same dict has). `Fraction` is not JSON
serializable, so:

  - `json.dumps(continuum.ranks)` crashes
  - `json.dumps(dataclasses.asdict(continuum))` crashes
  - `json.dumps(continuum.rank(anon_name))` crashes

...for ANY continuum that has been through even one `densify_between`
call, integer-valued mediant or not.

Today this is DORMANT, not a live crash: the app's only JSON render path
(`dazzlecmd_lib.interrogation.render_interrogation(..., as_json=True)`)
serializes rung NAMES (strings) into the payload, never the raw
`.ranks` dict or the dataclass itself, and no LIVE production continuum
(VERB_SPACE, LEVEL_CONTINUUM, KIT_PRESENCE_SPACE, VISIBILITY_CONTINUUM)
is ever densified at runtime today. But it is a real landmine for the
next consumer that serializes a densified continuum directly (a debug
dump, a `--json --verbose` deep view, a future persistence path) --
flagging per the cross-layer numeric-addressing probe.

Run: python tests/one-offs/repro_densified_ranks_break_json_serialization.py
"""
import dataclasses
import json
import sys

from dazzle_lib.continuum import Continuum


def main() -> int:
    failures = []

    # Whole-number mediant -- densify_between(-1, 1) gives anon "0".
    c = Continuum("v", ranks={"a": -1, "b": 1})
    c2 = c.densify_between("a", "b")
    print(f"anon '0' rank type: {type(c2.rank('0')).__name__} "
          f"(sibling 'a' rank type: {type(c2.rank('a')).__name__})")

    for label, fn in [
        ("json.dumps(ranks)", lambda: json.dumps(c2.ranks)),
        ("json.dumps(asdict(continuum))",
         lambda: json.dumps(dataclasses.asdict(c2))),
        ("json.dumps(rank('0'))", lambda: json.dumps(c2.rank("0"))),
    ]:
        try:
            fn()
            print(f"{label}: OK (unexpectedly -- may be fixed)")
        except TypeError as exc:
            print(f"{label}: CRASH -- {exc}")
            failures.append(label)

    if failures:
        print(
            f"CONFIRMED: densified continuums are not JSON-serializable "
            f"via the standard encoder ({len(failures)}/3 paths crash), "
            f"even for a whole-number-mediant anon rung.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
