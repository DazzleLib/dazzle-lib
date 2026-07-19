"""Tests for version module."""

from dazzle_lib._version import (
    MAJOR, MINOR, PATCH, PHASE, PROJECT_PHASE,
    get_version, get_base_version, get_display_version, get_pip_version,
    __app_name__,
)


def test_app_name():
    assert __app_name__ == "dazzle-lib"


def test_version_components():
    assert isinstance(MAJOR, int)
    assert isinstance(MINOR, int)
    assert isinstance(PATCH, int)


def test_phase_valid():
    """PHASE is empty string (stable release) or a string like 'alpha', 'beta', 'rc1'."""
    assert isinstance(PHASE, str)


def test_get_version_returns_string():
    v = get_version()
    assert isinstance(v, str)
    assert len(v) > 0


def test_base_version_format():
    base = get_base_version()
    assert base.startswith(f"{MAJOR}.{MINOR}.{PATCH}")


def test_display_version_includes_project_phase():
    display = get_display_version()
    if PROJECT_PHASE and PROJECT_PHASE != "stable":
        assert PROJECT_PHASE.upper() in display
    else:
        assert display == get_base_version()


def test_pip_version_pep440():
    pip_v = get_pip_version()
    assert "-" not in pip_v
    if PHASE:
        assert any(c.isalpha() for c in pip_v.split(".")[-1])
    else:
        # a `.devN` tail is valid PEP 440 even without a phase --
        # fresh-checkout hook stamps derive `0.8.2.devN` and the old
        # all-digits assertion rejected them (HOMEBOX handoff finding,
        # 2026-07-19; red only on stamp shapes carrying .devN)
        base, _, dev = pip_v.partition(".dev")
        assert all(c.isdigit() or c == "." for c in base)
        assert dev == "" or dev.isdigit()
