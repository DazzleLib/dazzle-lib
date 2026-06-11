"""Protocol satisfaction + mixin behavior: a plain dataclass with to_dict/
from_dict/SCHEMA_VERSION satisfies Serializable WITHOUT subclassing anything --
the structural-typing promise the bedrock makes."""

import json
from dataclasses import dataclass
from typing import Any, Dict

from dazzle_lib import DazzleDataMixin, Serializable, Viewable


@dataclass
class SampleResult(DazzleDataMixin):
    SCHEMA_VERSION = 1
    name: str = "demo"
    count: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {"schema_version": self.SCHEMA_VERSION, "name": self.name,
                "count": self.count}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SampleResult":
        return cls(name=data["name"], count=data["count"])


class BareDuck:
    """No mixin, no inheritance -- pure structural satisfaction."""

    SCHEMA_VERSION = 2

    def to_dict(self):
        return {"x": 1}

    @classmethod
    def from_dict(cls, data):
        return cls()

    def summary(self):
        return "a bare duck"


def test_dataclass_with_mixin_satisfies_serializable():
    s = SampleResult()
    assert isinstance(s, Serializable)
    assert isinstance(s, Viewable)


def test_bare_class_satisfies_protocols_structurally():
    d = BareDuck()
    assert isinstance(d, Serializable)
    assert isinstance(d, Viewable)


def test_non_conforming_object_rejected():
    assert not isinstance(object(), Serializable)
    assert not isinstance(object(), Viewable)


def test_round_trip():
    s = SampleResult(name="rt", count=7)
    again = SampleResult.from_dict(s.to_dict())
    assert again == s


def test_mixin_to_json_and_str():
    s = SampleResult(name="js", count=1)
    parsed = json.loads(s.to_json())
    assert parsed == {"schema_version": 1, "name": "js", "count": 1}
    assert json.loads(str(s)) == parsed


def test_mixin_summary_is_one_line():
    s = SampleResult()
    assert "\n" not in s.summary()
    assert "SampleResult" in s.summary()


def test_payload_typeddicts_are_constructible():
    from dazzle_lib import FileMetadataDict, TimestampsDict

    ts: TimestampsDict = {"modified": 1.0, "accessed": 2.0, "created": 3.0}
    md: FileMetadataDict = {"mode": 0o644, "size": 10, "timestamps": ts}
    assert md["timestamps"]["modified"] == 1.0
