"""dazzle-lib -- the DazzleLib stack's bedrock.

Shared Protocols, TypedDict payload schemas, the exception root, AND the pure
computational PRIMITIVES that every ``dazzle-*`` library composes on (the
``Continuum`` signed-axis primitive + ``ContinuumSpace``). Stdlib-only forever
and, by charter, SIDE-EFFECT-FREE: no I/O, no path handling, no platform probing,
no subprocess.

Charter evolution (0.2 -> 0.3): from "types only" to "types + pure primitives".
Pure computation over data (a Continuum's ordering, stepping, slicing) is
in-charter; side effects never are. The hard guarantees the charter test enforces
(stdlib-only + no behavior-bearing imports + no ``open()``) are UNCHANGED -- the
primitives pass them. The why: the stack needs shared *composable primitives*,
not only contract types, so tools compose on one Continuum/state-system instead
of re-implementing it (proven in dazzlecmd's Groupable<->Continuum unification).
See CHANGELOG. Architecture contract:
https://github.com/DazzleLib/.github/blob/main/docs/STACK-MAP.md
"""

from ._version import PIP_VERSION, __app_name__, __version__
from .exceptions import (
    DazzleError,
    FileOperationError,
    LinkError,
    PathIdentityError,
    PreserveError,
)
from .mixins import DazzleDataMixin
from .payloads import (
    FileMetadataDict,
    HashResultDict,
    LinkTargetDict,
    TimestampsDict,
    UnixMetadataDict,
    WindowsMetadataDict,
)
from .protocols import PathVariantResolver, Serializable, Viewable
from .continuum import (
    Continuum,
    ContinuumBoundaryError,
    ContinuumError,
    ContinuumProtocol,
    ContinuumSpace,
    ContinuumSpaceProtocol,
)

__all__ = [
    "__version__",
    "__app_name__",
    "PIP_VERSION",
    # protocols
    "Viewable",
    "Serializable",
    "PathVariantResolver",
    # payload schemas
    "TimestampsDict",
    "WindowsMetadataDict",
    "UnixMetadataDict",
    "FileMetadataDict",
    "LinkTargetDict",
    "HashResultDict",
    # exceptions
    "DazzleError",
    "PathIdentityError",
    "FileOperationError",
    "LinkError",
    "PreserveError",
    # mixin
    "DazzleDataMixin",
    # pure primitives (0.3+) -- the Continuum signed-axis + its space
    "Continuum",
    "ContinuumSpace",
    "ContinuumProtocol",
    "ContinuumSpaceProtocol",
    "ContinuumError",
    "ContinuumBoundaryError",
]
