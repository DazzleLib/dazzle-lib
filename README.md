# dazzle-lib

[![PyPI](https://img.shields.io/pypi/v/dazzle-lib?color=green)](https://pypi.org/project/dazzle-lib/)
[![Release Date](https://img.shields.io/github/release-date/DazzleLib/dazzle-lib?color=green)](https://github.com/DazzleLib/dazzle-lib/releases)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Installs](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/djdarcy/4ad3247ec3775486258d9e4fb81ae38a/raw/installs.json)](https://dazzlelib.github.io/dazzle-lib/stats/#installs)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20BSD-lightgrey.svg)](docs/platform-support.md)

**The DazzleLib stack's bedrock: shared Protocols, TypedDict payload schemas, the exception root, and the pure stdlib primitives (`Continuum` + the state system) every dazzle-\* tool composes on.**

Every `dazzle-*` library ([the stack](https://github.com/DazzleLib/.github/blob/main/docs/STACK-MAP.md)) builds on this package: it defines what stack objects can be expected to do (view themselves, serialize themselves), what shapes cross-layer payloads have, and (as of v0.3.x) the pure computational **primitives** they compose on. 

**Types + pure primitives** -- by charter this package is stdlib-only and SIDE-EFFECT-FREE forever (no I/O, no path handling, no platform probing, no subprocess). Pure computation over data (a `Continuum`'s ordering / stepping / slicing) is in-charter; side effects never are. (The charter evolved 0.2 -> 0.3 from "types only" to "types + pure primitives" -- the stack needs shared *composable* primitives, not only contract types. The hard guarantees, enforced by `tests/test_charter.py`, are unchanged.)

```bash
pip install dazzle-lib
```

## What's inside (all of it)

| Module | Contents |
|---|---|
| `dazzle_lib.protocols` | `Viewable` (`summary()`/`__str__`), `Serializable` (`to_dict`/`from_dict`/`to_json`, `SCHEMA_VERSION`), `PathVariantResolver` (`variants(path)` -- a path's alternative names, e.g. UNC <-> mapped drive) -- structural `Protocol`s, `runtime_checkable`, nothing is forced to subclass |
| `dazzle_lib.payloads` | The cross-layer TypedDict schemas: `FileMetadataDict`, `TimestampsDict`, `WindowsMetadataDict`, `UnixMetadataDict`, `LinkTargetDict`, `HashResultDict` -- mirroring what `dazzle-filekit` actually produces |
| `dazzle_lib.exceptions` | `DazzleError` root + per-domain bases (`PathIdentityError`, `FileOperationError`, `LinkError`, `PreserveError`) |
| `dazzle_lib.mixins` | `DazzleDataMixin` -- derives `to_json`/`summary`/`__str__` from your `to_dict` |
| `dazzle_lib.continuum` (0.3+) | `Continuum` -- the signed ordered-axis primitive (invariant-bearing zero, warm/cold lens, THAC0 threshold gate, channel backing) -- and `ContinuumSpace` -- N parallel Continuums on one presence scale (`slice`, `cascade_to_neutral`, cross-axis navigation, `describe`). Plus their structural `Protocol`s. Pure, stdlib-only, side-effect-free |
| `dazzle_lib.states` (0.4+) | The generic state-system machinery: `StateAxis` (a dimension; HAS-A optional `Continuum`), `EntityState` (an OBSERVED-not-stored snapshot; a point in a `ContinuumSpace`), `Transition` / `CompositeTransition` (declared edges + ordered multi-axis composition, with the `Reversibility` criticality algebra), `TransitionRegistry` (the criticality tables, queryable), `assert_round_trip` (the `group o ungroup = identity` contract executable), `observe`. The vocabulary; the consumer DECLARES its own axes/edges. Pure, stdlib + `Continuum` only |

> **New to the `Continuum` model?** [**The ladder**](docs/the-ladder.md) explains the four base objects (`Unified` / `Groupable` / `Continuum` / `ContinuumSpace`), the implicit-carry chain, the signed invariant-bearing zero, and aligned-vs-product composition.

## The idea: the dict is the interface

Rich objects in upper layers know how to become plain dicts; lower-layer functions take and return those dicts. The TypedDicts here are the agreed shapes, so a manifest object in `dazzle-preservelib` and a metadata collector in `dazzle-filekit` speak the same payload without sharing a class hierarchy:

```python
from dataclasses import dataclass
from dazzle_lib import DazzleDataMixin, Serializable, FileMetadataDict

@dataclass
class TransferResult(DazzleDataMixin):
    SCHEMA_VERSION = 1
    path: str
    metadata: FileMetadataDict

    def to_dict(self):
        return {"schema_version": self.SCHEMA_VERSION,
                "path": self.path, "metadata": dict(self.metadata)}

    @classmethod
    def from_dict(cls, data):
        # from_dict is the boundary -- VALIDATE here, don't just reconstruct.
        # A bare cls(**data) re-imports the "nothing to validate against" bug.
        return cls(path=data["path"], metadata=data["metadata"])

result = TransferResult("a.txt", {"mode": 0o644, "size": 10, "timestamps": {}})
assert isinstance(result, Serializable)   # structural -- no subclassing needed
print(result.summary())                   # one-liner for logs
```

And one catchable root for the whole stack:

```python
from dazzle_lib import DazzleError
try:
    ...  # any dazzle-* library call
except DazzleError as e:
    ...  # caught, whichever layer raised it
```

### Dict at the boundary, typed object inside

"The dict is the interface" is a **boundary** rule, not a working-representation rule. Confuse the two -- start computing against the dict instead of just handing it across a seam -- and you give up the schema that makes a mistake surface at the boundary instead of silently, three layers downstream. The plain dict is the *wire format* between independently-versioned libraries, so `dazzle-filekit` and `dazzle-preservelib` exchange a `FileMetadataDict` without sharing a class hierarchy. It is **not** an invitation to thread raw dicts through a library's internals: each side reconstructs its OWN typed object at `from_dict` and works with that. Pass a dict *across* the boundary; never reach for `d["key"]` deep in your code.

Two consequences, stated outright because the stack learned them the hard way:

- **`from_dict` should VALIDATE, not just reconstruct.** A `TypedDict` is statically-checkable but has *no* runtime enforcement -- at runtime it is a plain dict. The boundary is the safety net: `from_dict` is where an incoming payload becomes a *checked* typed object. A bare `cls(**data)` reintroduces exactly the "nothing to validate against, miss it downstream" failure that typed objects exist to prevent. (Reference pattern: dazzlecmd reconstructs every entity through Pydantic `validate_python` at its manifest boundary.)
- **The computational primitives are typed objects, not dicts.** `Continuum`, the state-system types (`StateAxis` / `EntityState` / `Transition`), and `Receipt` are frozen dataclasses -- the dict idiom above is for cross-library *payloads*, not for the shared machinery. Reach for a dict only at a serialization boundary or a genuinely open/extensible keyspace (validated at construction); reach for a typed object everywhere else.

## The charter (enforced by tests)

This package is **stdlib-only forever** and contains **no behavior**. `tests/test_charter.py` fails on any banned import (`os`, `shutil`, `pathlib`, `subprocess`, ...) anywhere in the package -- a PR that needs to weaken that test is adding something that belongs in a higher layer. Admission follows the **rule of two**: a Protocol or TypedDict enters the bedrock only when two or more stack libraries need it.

## The stack

| Layer | Library | Role |
|---|---|---|
| B | **dazzle-lib** (this) | bedrock contracts |
| L0 | [dazzle-unctools](https://github.com/DazzleLib/UNCtools) | path identity (UNC/drive/origin) |
| L1 | [dazzle-filekit](https://github.com/DazzleLib/dazzle-filekit) | filesystem primitives |
| L2 | dazzle-linklib *(planned)* | link serialization |
| L3 | dazzle-preservelib *(planned)* | operation orchestration |
| ⊥ | [dazzle-treelib](https://github.com/DazzleLib/dazzle-tree-lib) | traversal engine |

Full architecture contract: [STACK-MAP.md](https://github.com/DazzleLib/.github/blob/main/docs/STACK-MAP.md). API stability policy: [docs/api-stability.md](docs/api-stability.md).

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

Before proposing additions, note the two house rules this package lives by:
- **The charter**: types only -- no I/O, no path handling, no behavior (`tests/test_charter.py` enforces it; a PR that needs to weaken that test belongs in a higher layer)
- **The rule of two**: a Protocol or TypedDict enters the bedrock only when two or more stack libraries need it
- API changes follow **[docs/api-stability.md](docs/api-stability.md)** (locked surface, noisy-shim deprecation policy)

Like the project?

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/djdarcy)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. The bedrock sits beneath MIT and GPL stack members alike, so it carries the permissive license.
