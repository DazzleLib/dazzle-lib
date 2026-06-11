"""``python -m dazzle_lib`` -- print version and charter (a library, not a tool)."""

from ._version import DISPLAY_VERSION, __app_name__

if __name__ == "__main__":
    print(f"{__app_name__} {DISPLAY_VERSION}")
    print(
        "The DazzleLib stack's bedrock: Protocols, TypedDict payload schemas, "
        "and the exception root.\nTypes only -- by charter this package "
        "contains no behavior. https://github.com/DazzleLib/dazzle-lib"
    )
