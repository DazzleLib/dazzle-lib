"""TypedDict payload schemas shared across the DazzleLib stack.

These are THE cross-layer payload shapes (STACK-MAP D10): when one stack
library hands file metadata, timestamps, link descriptions, or hash results to
another, the value conforms to a shape defined here. Rich objects in upper
layers serialize themselves INTO these shapes; primitive functions in lower
layers take and return them directly.

The shapes are not invented -- they mirror what ``dazzle-filekit`` actually
produces today (``collect_file_metadata`` / ``collect_timestamp_info`` /
``calculate_file_hash``), so adopting them is a typing change, not a behavior
change. Admission policy (rule of two): a shape lives here only once two or
more stack libraries need it.

Charter reminder: this module is types-only. No I/O, no behavior.
"""

from typing import Dict, Optional, TypedDict

__all__ = [
    "TimestampsDict",
    "WindowsMetadataDict",
    "UnixMetadataDict",
    "FileMetadataDict",
    "LinkTargetDict",
    "HashResultDict",
]


class TimestampsDict(TypedDict, total=False):
    """File timestamps, epoch floats plus ISO-8601 projections.

    Mirrors ``dazzle_filekit.metadata.collect_timestamp_info``. Note that
    ``created`` carries ``st_ctime``, which is creation time on Windows but
    inode-change time on Unix -- consumers must not assume birth-time
    semantics cross-platform.
    """

    created: float
    modified: float
    accessed: float
    created_iso: str
    modified_iso: str
    accessed_iso: str


class WindowsMetadataDict(TypedDict, total=False):
    """Windows-specific metadata (mirrors filekit's ``_collect_windows_metadata``).

    With pywin32 available the rich fields are present (``attributes``,
    owner/group + SIDs, ``security_descriptor_sddl``); without it the
    ``attrib``-fallback path fills only the boolean flags and
    ``attrib_output``. ``security_descriptor_sddl`` may be present-but-None
    when the descriptor could not be stringified.
    """

    attributes: int
    is_hidden: bool
    is_system: bool
    is_readonly: bool
    is_archive: bool
    owner: str
    group: str
    owner_sid: str
    group_sid: str
    security_descriptor_sddl: Optional[str]
    attrib_output: str


class UnixMetadataDict(TypedDict, total=False):
    """Unix-specific metadata (mirrors filekit's unix branch)."""

    uid: int
    gid: int


class _FileMetadataRequired(TypedDict):
    mode: int
    size: int
    timestamps: TimestampsDict


class FileMetadataDict(_FileMetadataRequired, total=False):
    """A file's preservable metadata snapshot.

    Mirrors ``dazzle_filekit.metadata.collect_file_metadata``: ``mode``,
    ``size``, and ``timestamps`` are always present; exactly one of
    ``windows`` / ``unix`` appears depending on platform; ``xattrs`` (name ->
    base64-encoded value) appears on Unix when extended attributes exist.
    """

    windows: WindowsMetadataDict
    unix: UnixMetadataDict
    xattrs: Dict[str, str]


class LinkTargetDict(TypedDict, total=False):
    """An intrinsic description of a filesystem link, as data.

    The cross-layer shape for "what is this link": produced by link analysis
    (dazzle-filekit's ``analyze_link``), embedded in serialized link files
    (dazzle-linklib), and consumed by orchestration policy (dazzle-preservelib).
    Intrinsic properties only -- anything relative to a specific operation
    (e.g. "does this link point inside the move destination") is computed at
    the orchestration layer and does NOT belong here.

    ``kind`` is one of ``"symlink"``, ``"junction"``, ``"hardlink"``.
    ``raw_target`` is the stored target text exactly as written; ``resolved_target``
    is its absolute resolution (when resolvable). ``target_is_directory`` is
    best-effort (False when the target is missing).
    """

    kind: str
    raw_target: str
    resolved_target: str
    is_broken: bool
    is_circular: bool
    target_is_directory: bool


HashResultDict = Dict[str, str]
"""Hash results keyed by algorithm name, hex digests as values.

Mirrors ``dazzle_filekit.verification.calculate_file_hash`` (e.g.
``{"sha256": "ab12...", "md5": "cd34..."}``). A plain ``Dict`` alias rather
than a TypedDict because the key set is open (any hashlib algorithm).
"""
