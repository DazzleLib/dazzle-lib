"""The one permitted mixin: derive presentation from ``to_dict``.

:class:`DazzleDataMixin` is convenience, not contract -- objects may satisfy
the protocols without it. It exists so simple data objects don't each rewrite
``to_json``/``__str__``/``summary`` plumbing. Anything fancier belongs in the
object itself, not here (charter: this module stays this small).
"""

import json
from typing import Any, Dict

__all__ = ["DazzleDataMixin"]


class DazzleDataMixin:
    """Derives ``to_json``, ``summary`` and ``__str__`` from ``to_dict``.

    The host class supplies ``to_dict()`` (and thereby decides what is
    JSON-safe); the mixin only formats. Combined with a ``from_dict``
    classmethod and a ``SCHEMA_VERSION`` attribute, a host class satisfies
    both :class:`~dazzle_lib.protocols.Serializable` and
    :class:`~dazzle_lib.protocols.Viewable`.
    """

    def to_dict(self) -> Dict[str, Any]:  # pragma: no cover - host overrides
        raise NotImplementedError(
            f"{type(self).__name__} must implement to_dict() to use DazzleDataMixin"
        )

    def to_json(self, *, indent: int = 2, sort_keys: bool = False) -> str:
        """JSON form of :meth:`to_dict` (``default=str`` catches stragglers)."""
        return json.dumps(
            self.to_dict(), indent=indent, sort_keys=sort_keys, default=str
        )

    def summary(self) -> str:
        """One-line description: class name plus top-level keys."""
        keys = ", ".join(list(self.to_dict().keys())[:6])
        return f"{type(self).__name__}({keys})"

    def __str__(self) -> str:
        return self.to_json()
