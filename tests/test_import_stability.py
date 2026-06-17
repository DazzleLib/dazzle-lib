"""Import-stability canary (see docs/api-stability.md).

Every symbol listed here is part of the locked public API. If this test
fails, a consumer somewhere breaks: do NOT silently fix the test -- follow
the api-stability.md process (deprecate with a noisy shim, register it,
slate removal).
"""

import importlib

LOCKED_SURFACE = {
    "dazzle_lib": [
        "__version__",
        "__app_name__",
        "Viewable",
        "Serializable",
        "PathVariantResolver",
        "TimestampsDict",
        "WindowsMetadataDict",
        "UnixMetadataDict",
        "FileMetadataDict",
        "LinkTargetDict",
        "HashResultDict",
        "DazzleError",
        "PathIdentityError",
        "FileOperationError",
        "LinkError",
        "PreserveError",
        "DazzleDataMixin",
    ],
    "dazzle_lib.protocols": ["Viewable", "Serializable", "PathVariantResolver"],
    "dazzle_lib.payloads": [
        "TimestampsDict",
        "WindowsMetadataDict",
        "UnixMetadataDict",
        "FileMetadataDict",
        "LinkTargetDict",
        "HashResultDict",
    ],
    "dazzle_lib.exceptions": [
        "DazzleError",
        "PathIdentityError",
        "FileOperationError",
        "LinkError",
        "PreserveError",
    ],
    "dazzle_lib.mixins": ["DazzleDataMixin"],
}


def test_locked_surface_importable():
    missing = []
    for module_name, symbols in LOCKED_SURFACE.items():
        module = importlib.import_module(module_name)
        for symbol in symbols:
            if not hasattr(module, symbol):
                missing.append(f"{module_name}.{symbol}")
    assert not missing, (
        f"Locked API symbols missing: {missing} -- see docs/api-stability.md "
        f"before changing the public surface."
    )


def test_exception_hierarchy_rooted():
    from dazzle_lib import (
        DazzleError,
        FileOperationError,
        LinkError,
        PathIdentityError,
        PreserveError,
    )
    for exc in (PathIdentityError, FileOperationError, LinkError, PreserveError):
        assert issubclass(exc, DazzleError)
    assert issubclass(DazzleError, Exception)
