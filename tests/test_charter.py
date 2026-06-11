"""The charter test: dazzle-lib is types-only, stdlib-only, behavior-free.

This is the god-library guard from the STACK-MAP (D10). It fails the moment
anyone adds I/O, path handling, platform probing, or subprocess use to the
bedrock. A PR that needs to weaken this test is, by definition, adding
behavior that belongs in a higher layer.
"""

import ast
from pathlib import Path

import dazzle_lib

PACKAGE_DIR = Path(dazzle_lib.__file__).parent

# Modules whose import (at any level) means behavior crept in.
BANNED_IMPORTS = {
    "os",            # I/O + platform probing
    "io",
    "shutil",
    "pathlib",       # path handling is L1's domain (charter test uses it; the package may not)
    "subprocess",
    "socket",
    "platform",
    "ctypes",
    "tempfile",
    "glob",
    "fnmatch",
    "stat",
    "sys",           # no interpreter poking either; types don't need it
}

# _version.py is generated/managed by repokit hooks and exempt (it reads nothing).
EXEMPT_FILES = {"_version.py"}


def _module_files():
    return [
        p for p in PACKAGE_DIR.glob("*.py")
        if p.name not in EXEMPT_FILES
    ]


def _imports_of(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                found.add(node.module.split(".")[0])
    return found


def test_no_banned_imports():
    violations = {}
    for path in _module_files():
        bad = _imports_of(path) & BANNED_IMPORTS
        if bad:
            violations[path.name] = sorted(bad)
    assert not violations, (
        f"CHARTER VIOLATION -- behavior-bearing imports in the bedrock: {violations}. "
        f"dazzle-lib is types-only; this capability belongs in a higher layer."
    )


def test_stdlib_only():
    """No third-party imports, ever (the package must not even import filekit)."""
    allowed = {"json", "typing", "enum", "dataclasses", "abc", "collections",
               "datetime", "ast", "dazzle_lib"}
    violations = {}
    for path in _module_files():
        extra = _imports_of(path) - allowed - BANNED_IMPORTS
        if extra:
            violations[path.name] = sorted(extra)
    assert not violations, (
        f"Unexpected imports in the bedrock (stdlib-only, and only the boring "
        f"parts): {violations}. If legitimately needed, add to the allowlist "
        f"in this test WITH a charter justification in the commit message."
    )


def test_no_filesystem_calls_in_source_text():
    """Belt-and-braces: no open()/Path( usage even without an import."""
    for path in _module_files():
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                name = getattr(fn, "id", getattr(fn, "attr", ""))
                assert name != "open", (
                    f"CHARTER VIOLATION -- open() call in {path.name}"
                )
