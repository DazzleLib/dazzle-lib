# API Stability

dazzle-lib is the bedrock of the DazzleLib stack: every `dazzle-*` library may
import it, so its public surface is **locked from the first release**. The
canary test `tests/test_import_stability.py` enumerates the locked symbols and
fails if any disappears or moves.

## Policy

1. **Locked symbols never vanish silently.** Removing or renaming one follows
   the stack's shim policy (STACK-MAP Rule 6): a temporary NOISY shim
   (`DeprecationWarning` naming the new home and removal version), registered
   in the stack's alias register, removed on schedule.
2. **TypedDict shapes only gain keys.** Removing or re-typing an existing key
   is a breaking change requiring a `SCHEMA_VERSION`-style migration note in
   the CHANGELOG and coordination with every consumer listed below.
3. **Additions follow the rule of two**: a Protocol/TypedDict enters the
   bedrock only when two or more stack libraries need it.
4. **The charter is not negotiable**: no behavior, no I/O, no non-stdlib
   imports -- `tests/test_charter.py` enforces it; weakening that test is an
   architecture change, not a code review comment.

## Locked surface (v0.1.0)

| Module | Symbols |
|---|---|
| `dazzle_lib` (re-exports) | everything below + `__version__`, `__app_name__` |
| `dazzle_lib.protocols` | `Viewable`, `Serializable` |
| `dazzle_lib.payloads` | `TimestampsDict`, `WindowsMetadataDict`, `UnixMetadataDict`, `FileMetadataDict`, `LinkTargetDict`, `HashResultDict` |
| `dazzle_lib.exceptions` | `DazzleError`, `PathIdentityError`, `FileOperationError`, `LinkError`, `PreserveError` |
| `dazzle_lib.mixins` | `DazzleDataMixin` |

## Known consumers

| Consumer | Symbols | Since |
|---|---|---|
| dazzle-filekit (planned, 0.3.0 / stack P1) | payload TypedDicts as metadata/timestamp signatures | stack phase P1 |
| dazzle-unctools (planned, 0.2.0 / stack P1) | `DazzleError`, `PathIdentityError` | stack phase P1 |
| dazzle-linklib (planned / stack P2) | `Serializable`, `LinkTargetDict`, `LinkError`, `DazzleDataMixin` | stack phase P2 |
| dazzle-preservelib (planned / stack P3) | `Serializable`, `FileMetadataDict`, `PreserveError`, `DazzleDataMixin` | stack phase P3 |

Update this table whenever a consumer adopts a symbol -- it is the blast-radius
map for any proposed change.
