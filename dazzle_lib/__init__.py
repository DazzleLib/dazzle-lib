"""dazzle-lib -- the DazzleLib stack's bedrock.

Shared Protocols, TypedDict payload schemas, and the exception root that every
``dazzle-*`` library builds on. Types only: this package is stdlib-only forever
and, by charter, contains no I/O, no path handling, no platform probing, and no
"utils". See the architecture contract:
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
from .protocols import Serializable, Viewable

__all__ = [
    "__version__",
    "__app_name__",
    "PIP_VERSION",
    # protocols
    "Viewable",
    "Serializable",
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
]
