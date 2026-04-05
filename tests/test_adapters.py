"""Tests for all platform adapters."""

from datetime import datetime
from pathlib import Path

import pytest

from weave.core.adapters.base import BaseAdapter
from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.adapters.cursor import CursorAdapter
from weave.core.schema import Skill

CLAUDE_FIXTURES = Path(__file__).parent / "fixtures" / "claude_code"
CURSOR_FIXTURES = Path(__file__).parent / "fixtures" / "cursor"


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


# ---------------------------------------------------------------------------
# ClaudeCodeAdapter tests
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> ClaudeCodeAdapter:
    """Return a fresh ClaudeCodeAdapter instance for each test."""
    return ClaudeCodeAdapter()


@pytest.fixture
def cursor_adapter() -> CursorAdapter:
    """Return a fresh CursorAdapter instance for each test."""
    return CursorAdapter()


def test_claude_load_returns_all_skills_from_directory(adapter: ClaudeCodeAdapter) -> None:
    """load() returns one Skill per .md file found in the fixtures directory."""
    skills = adapter.load(str(CLAUDE_FIXTURES))
    assert len(skills) == 2


def test_claude_load_parses_frontmatter_name(adapter: ClaudeCodeAdapter) -> None:
    """load() correctly reads the name field from YAML frontmatter."""
    skills = adapter.load(str(CLAUDE_FIXTURES))
    names = {s.name for s in skills}
    assert "Backend API Engineer" in names


def test_claude_load_falls_back_to_filename_when_no_frontmatter(
    adapter: ClaudeCodeAdapter, tmp_path: Path
) -> None:
    """load() uses the file stem as name when no YAML frontmatter is present."""
    md_file = tmp_path / "my_skill.md"
    md_file.write_text("This skill handles data processing tasks.\n\nMore content here.")
    skills = adapter.load(str(tmp_path))
    assert skills[0].name == "my_skill"


def test_claude_load_handles_empty_file_without_crashing(
    adapter: ClaudeCodeAdapter, tmp_path: Path
) -> None:
    """load() skips empty .md files and returns an empty list without raising."""
    (tmp_path / "empty.md").write_text("")
    skills = adapter.load(str(tmp_path))
    assert skills == []


def test_claude_load_returns_empty_list_for_directory_with_no_md_files(
    adapter: ClaudeCodeAdapter, tmp_path: Path
) -> None:
    """load() returns an empty list when the directory contains no .md files."""
    skills = adapter.load(str(tmp_path))
    assert skills == []


def test_claude_detect_returns_true_for_directory_with_md_files(
    adapter: ClaudeCodeAdapter,
) -> None:
    """detect() returns True for the claude_code fixtures directory."""
    assert adapter.detect(str(CLAUDE_FIXTURES)) is True


# ---------------------------------------------------------------------------
# CursorAdapter tests
# ---------------------------------------------------------------------------


def test_cursor_load_returns_all_skills_from_directory(
    cursor_adapter: CursorAdapter,
) -> None:
    """load() returns one Skill per cursor file found (cursorrules + mdc)."""
    skills = cursor_adapter.load(str(CURSOR_FIXTURES))
    assert len(skills) == 2


def test_cursor_load_parses_cursorrules_name(cursor_adapter: CursorAdapter) -> None:
    """load() uses the file stem as name for plain .cursorrules files."""
    skills = cursor_adapter.load(str(CURSOR_FIXTURES))
    names = {s.name for s in skills}
    assert "frontend" in names


def test_cursor_load_parses_mdc_frontmatter_description(
    cursor_adapter: CursorAdapter,
) -> None:
    """load() uses the MDC frontmatter description as trigger_context."""
    skills = cursor_adapter.load(str(CURSOR_FIXTURES))
    mdc_skill = next(s for s in skills if s.metadata.get("format") == "mdc")
    assert "TypeScript" in mdc_skill.trigger_context


def test_cursor_load_handles_empty_file_without_crashing(
    cursor_adapter: CursorAdapter, tmp_path: Path
) -> None:
    """load() skips empty .cursorrules files and returns an empty list."""
    (tmp_path / "rules.cursorrules").write_text("")
    skills = cursor_adapter.load(str(tmp_path))
    assert skills == []


def test_cursor_load_returns_empty_list_for_directory_with_no_cursor_files(
    cursor_adapter: CursorAdapter, tmp_path: Path
) -> None:
    """load() returns an empty list when no .cursorrules or .mdc files exist."""
    skills = cursor_adapter.load(str(tmp_path))
    assert skills == []


def test_cursor_detect_returns_true_for_directory_with_cursorrules(
    cursor_adapter: CursorAdapter,
) -> None:
    """detect() returns True for the cursor fixtures directory."""
    assert cursor_adapter.detect(str(CURSOR_FIXTURES)) is True
