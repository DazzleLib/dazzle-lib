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

from typing import Any, Dict, Protocol, runtime_checkable

__all__ = ["Viewable", "Serializable"]


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
