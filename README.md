# dazzle-lib

**The DazzleLib stack's bedrock: shared Protocols, TypedDict payload schemas, and the exception root.**

[![PyPI](https://img.shields.io/pypi/v/dazzle-lib)](https://pypi.org/project/dazzle-lib/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://pypi.org/project/dazzle-lib/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-all-brightgreen)](docs/platform-support.md)

Every `dazzle-*` library ([the stack](https://github.com/DazzleLib/.github/blob/main/docs/STACK-MAP.md)) builds on this package: it defines what stack objects can be expected to do (view themselves, serialize themselves) and what shapes cross-layer payloads have. **Types only** -- by charter this package contains no I/O, no path handling, no platform probing, and no behavior, forever.

```bash
pip install dazzle-lib
```

## What's inside (all of it)

| Module | Contents |
|---|---|
| `dazzle_lib.protocols` | `Viewable` (`summary()`/`__str__`), `Serializable` (`to_dict`/`from_dict`/`to_json`, `SCHEMA_VERSION`) -- structural `Protocol`s, `runtime_checkable`, nothing is forced to subclass |
| `dazzle_lib.payloads` | The cross-layer TypedDict schemas: `FileMetadataDict`, `TimestampsDict`, `WindowsMetadataDict`, `UnixMetadataDict`, `LinkTargetDict`, `HashResultDict` -- mirroring what `dazzle-filekit` actually produces |
| `dazzle_lib.exceptions` | `DazzleError` root + per-domain bases (`PathIdentityError`, `FileOperationError`, `LinkError`, `PreserveError`) |
| `dazzle_lib.mixins` | `DazzleDataMixin` -- derives `to_json`/`summary`/`__str__` from your `to_dict` |

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

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## License

MIT -- the bedrock sits beneath MIT and GPL stack members alike, so it carries the permissive license.
