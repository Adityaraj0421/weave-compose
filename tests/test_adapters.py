"""Tests for all platform adapters."""

from datetime import datetime

import pytest

from weave.core.adapters.base import BaseAdapter
from weave.core.schema import Skill


class _ConcreteAdapter(BaseAdapter):
    """Minimal concrete subclass used to exercise BaseAdapter helper methods."""

    def load(self, path: str) -> list[Skill]:
        """Return an empty list — implementation not under test here."""
        return []


def test_base_adapter_cannot_be_instantiated_directly() -> None:
    """BaseAdapter raises TypeError when instantiated without implementing load()."""
    with pytest.raises(TypeError):
        BaseAdapter()  # type: ignore[abstract]


def test_generate_id_returns_unique_values() -> None:
    """_generate_id() returns a different string on each call."""
    adapter = _ConcreteAdapter()
    first = adapter._generate_id()
    second = adapter._generate_id()
    assert first != second


def test_timestamp_returns_valid_iso_format() -> None:
    """_timestamp() returns a UTC ISO 8601 string parseable by datetime.fromisoformat()."""
    adapter = _ConcreteAdapter()
    result = adapter._timestamp()
    # Raises ValueError if the string is not a valid ISO 8601 timestamp
    parsed = datetime.fromisoformat(result)
    assert result.endswith("+00:00"), f"Expected UTC offset '+00:00', got: {result!r}"
    assert parsed.tzinfo is not None
