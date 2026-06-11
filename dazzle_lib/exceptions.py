"""The DazzleLib exception bedrock.

One catchable root (:class:`DazzleError`) for the whole stack, plus one base
per layer domain. Each stack library derives ITS OWN exceptions from the
matching domain base (e.g. dazzle-preservelib's ``ManifestVersionError`` would
subclass :class:`PreserveError`), so consumers can choose their catch
granularity: a specific error, a domain, or the whole stack.

Charter reminder: these are plain exception types. No behavior beyond
``__init__``-style state, no I/O.
"""

__all__ = [
    "DazzleError",
    "PathIdentityError",
    "FileOperationError",
    "LinkError",
    "PreserveError",
]


class DazzleError(Exception):
    """Root of every exception raised by a DazzleLib stack library."""


class PathIdentityError(DazzleError):
    """Domain base for path-identity failures (dazzle-unctools, L0):
    UNC/drive mapping, origin classification, identity probing."""


class FileOperationError(DazzleError):
    """Domain base for filesystem-primitive failures (dazzle-filekit, L1):
    copy/move, metadata collect/apply, hashing, link creation."""


class LinkError(DazzleError):
    """Domain base for link-serialization failures (dazzle-linklib, L2):
    .dazzlelink parsing, export/import, rebase."""


class PreserveError(DazzleError):
    """Domain base for orchestration failures (dazzle-preservelib, L3):
    manifests, transactional copy/move/restore/verify, conflict policy."""
