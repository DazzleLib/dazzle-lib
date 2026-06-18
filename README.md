# dazzle-lib

**The DazzleLib stack's bedrock: shared Protocols, TypedDict payload schemas, the exception root, and the pure stdlib primitives (`Continuum`) every dazzle-\* tool composes on.**

[![PyPI](https://img.shields.io/pypi/v/dazzle-lib?color=green)](https://pypi.org/project/dazzle-lib/)
[![Release Date](https://img.shields.io/github/release-date/DazzleLib/dazzle-lib?color=green)](https://github.com/DazzleLib/dazzle-lib/releases)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Installs](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/djdarcy/4ad3247ec3775486258d9e4fb81ae38a/raw/installs.json)](https://dazzlelib.github.io/dazzle-lib/stats/#installs)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20BSD-lightgrey.svg)](docs/platform-support.md)

Every `dazzle-*` library ([the stack](https://github.com/DazzleLib/.github/blob/main/docs/STACK-MAP.md)) builds on this package: it defines what stack objects can be expected to do (view themselves, serialize themselves), what shapes cross-layer payloads have, and -- as of 0.3 -- the pure computational **primitives** they compose on. **Types + pure primitives** -- by charter this package is stdlib-only and SIDE-EFFECT-FREE forever (no I/O, no path handling, no platform probing, no subprocess). Pure computation over data (a `Continuum`'s ordering / stepping / slicing) is in-charter; side effects never are. (The charter evolved 0.2 -> 0.3 from "types only" to "types + pure primitives" -- the stack needs shared *composable* primitives, not only contract types; see the CHANGELOG for the why. The hard guarantees, enforced by `tests/test_charter.py`, are unchanged.)

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
