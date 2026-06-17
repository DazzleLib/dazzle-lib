"""Structural protocols every DazzleLib stack object is expected to satisfy.

These are :class:`typing.Protocol` definitions -- STRUCTURAL contracts, not base
classes. Nothing in the stack is required to subclass anything here; an object
satisfies a protocol simply by implementing its methods (and can be checked at
runtime with ``isinstance`` because both are ``@runtime_checkable``).

The design stance (STACK-MAP D10): "the dict is the interface; objects know how
to become dicts." Rich objects in upper layers (manifest, link-data, results)
serialize themselves INTO the plain TypedDict payload shapes defined in
:mod:`dazzle_lib.payloads`; lower-layer functions take and return those dicts.

Charter reminder: this module is types-only. No I/O, no behavior.
"""

from typing import Any, Dict, Protocol, Sequence, runtime_checkable

__all__ = ["Viewable", "Serializable", "PathVariantResolver"]


@runtime_checkable
class Viewable(Protocol):
    """An object that can present itself to a human.

    Expectations:

    - ``summary()`` returns a SHORT one-line description suitable for list
      views, log lines, and progress output.
    - ``__str__`` may be longer (multi-line is fine) but must never raise.
    """

    def summary(self) -> str:
        """One-line human-readable description of this object."""
        ...


@runtime_checkable
class Serializable(Protocol):
    """An object that can round-trip through a plain, JSON-safe dict.

    Expectations:

    - ``to_dict()`` returns a dict containing only JSON-safe values
      (str/int/float/bool/None/list/dict). Where a shared payload shape
      exists in :mod:`dazzle_lib.payloads`, the dict conforms to it.
    - ``from_dict(data)`` is a classmethod constructing an equivalent object.
    - ``SCHEMA_VERSION`` identifies the dict layout so readers can migrate
      old serialized forms. Bump it on any breaking shape change.
    """

    SCHEMA_VERSION: int

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe dict representation of this object."""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Serializable":
        """Construct an instance from a dict produced by :meth:`to_dict`."""
        ...


@runtime_checkable
class PathVariantResolver(Protocol):
    """Proposes alternative names for a path so an operation that fails under
    one name can be retried under another.

    The motivating case: on Windows a file often has two names -- a UNC form
    (``\\\\server\\share\\f``) and a mapped-drive form (``Z:\\f``) -- and a
    security zone can block opening/copying via one name while the other works,
    even though both *exist*. A resolver answers "what are this path's other
    names?" so the caller can retry the real operation under each.

    Design stance (STACK-MAP D7/D10 -- the documented ``path_variant_resolver``
    hook): this is identity KNOWLEDGE, not I/O. A resolver only *proposes*
    candidate path strings; it never opens, copies, stats, or otherwise touches
    the filesystem on the caller's behalf. The canonical implementation is the
    path-identity layer (unctools, L0). Upper layers (e.g. filekit, L1) accept a
    resolver so the variant-knowledge can come from any identity source and be
    swapped -- or faked in tests -- rather than reached through a shared object
    graph. Layers meet at this contract. (filekit's default resolver is
    unctools-backed; whether a given consumer treats that source as a hard or
    optional dependency is the consumer's call, not the Protocol's.)

    Expectations:

    - ``variants(path)`` returns candidate path strings to try, in priority
      order, and SHOULD include ``path`` itself (conventionally first). A
      resolver that knows no alternatives returns ``[path]`` -- a valid no-op.
      It MUST NOT return ``None``. Strings in, strings out (the dict/str is the
      interface; pathlib stays out of the bedrock).
    """

    def variants(self, path: str) -> "Sequence[str]":
        """Return candidate names for ``path`` (including ``path`` itself), in
        the order an operation should try them."""
        ...
