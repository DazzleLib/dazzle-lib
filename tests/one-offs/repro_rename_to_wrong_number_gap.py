"""FIXED 2026-07-05 (dazzle-lib 0.8.2 5bac072): the numeric-name truth
guard in Continuum.__post_init__ rejects both forms (constructor +
rename_level via reconstruction). Living regression:
test_nucleus_and_rank_addressing.py::TestTesterFindings0705. History below.
"""
"""Repro for the v0.8.1 bedrock checklist Section 4.1 / 4.3 pre-seeded
suspicion ("the rename-to-wrong-number gap") -- CONFIRMED REAL.

Neither `Continuum.rename_level()` nor the `Continuum` constructor guard
against a pure-numeric NAME that disagrees with the rung's actual rank.
Under rank addressing (`level_at`), a numeric-looking name IS treated as
an address for that rank -- so a rung named "5" sitting at rank 0 is a
live lie: `level_at(5)` will resolve to whatever rung ACTUALLY sits at
rank 5 (or error), never to this one, while `level_at(0)` resolves to
this rung whose own name claims to be "5". B3 (rank-addressing-as-name)
will make this ambiguity load-bearing rather than cosmetic.

Three ways in, all confirmed silent today:
  1. `rename_level` on an ANONYMOUS self-named rung to a wrong number.
  2. `rename_level` on a NAMED (non-anonymous) rung to a wrong number.
  3. Direct construction with a numeric-string key whose value disagrees.

Run: python tests/one-offs/repro_rename_to_wrong_number_gap.py
"""
import sys

from dazzle_lib.continuum import Continuum


def main() -> int:
    problems = []

    # 1. Anonymous rung, wrong-number christening.
    c = Continuum("v", ranks={"a": -1, "b": 1})
    c2 = c.densify_between("a", "b")  # anon "0"
    c3 = c2.rename_level("0", "5")  # should probably raise; doesn't
    if c3.rank("5") != 5:
        problems.append(
            f"rename_level('0','5') succeeded silently: rung '5' has "
            f"rank {c3.rank('5')!r}, not 5"
        )

    # 2. Named (non-anonymous) rung, wrong-number rename.
    c4 = c2.rename_level("a", "7")
    if c4.rank("7") != 7:
        problems.append(
            f"rename_level('a','7') succeeded silently: rung '7' has "
            f"rank {c4.rank('7')!r}, not 7"
        )

    # 3. Direct construction with a lying numeric-string key.
    c5 = Continuum("x", ranks={"3": 0})
    if c5.rank("3") != 3:
        problems.append(
            f"Continuum(ranks={{'3': 0}}) constructed silently: rung "
            f"'3' has rank {c5.rank('3')!r}, not 3"
        )

    if problems:
        print("CONFIRMED -- the rename/construct-to-wrong-number gap is real:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("not reproduced (all three now guarded) -- gap appears fixed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
