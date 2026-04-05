"""Tests for the WindsurfAdapter."""

from pathlib import Path

import pytest

from weave.core.adapters.windsurf import WindsurfAdapter

WINDSURF_FIXTURES = Path(__file__).parent / "fixtures" / "windsurf"


@pytest.fixture
def windsurf_adapter() -> WindsurfAdapter:
    """Return a fresh WindsurfAdapter instance for each test."""
    return WindsurfAdapter()


def test_windsurf_load_returns_all_skills_from_directory(
    windsurf_adapter: WindsurfAdapter,
) -> None:
    """load() returns one Skill per .windsurfrules file found in the fixtures dir."""
    skills = windsurf_adapter.load(str(WINDSURF_FIXTURES))
    assert len(skills) == 2


def test_windsurf_load_parses_name_from_file_stem(
    windsurf_adapter: WindsurfAdapter,
) -> None:
    """load() uses the file stem as the Skill name."""
    skills = windsurf_adapter.load(str(WINDSURF_FIXTURES))
    names = {s.name for s in skills}
    assert "python_standards" in names


def test_windsurf_load_parses_first_paragraph_as_trigger_context(
    windsurf_adapter: WindsurfAdapter,
) -> None:
    """load() uses the first paragraph of content as trigger_context."""
    skills = windsurf_adapter.load(str(WINDSURF_FIXTURES))
    python_skill = next(s for s in skills if s.name == "python_standards")
    assert "Python" in python_skill.trigger_context


def test_windsurf_load_handles_empty_file_without_crashing(
    windsurf_adapter: WindsurfAdapter, tmp_path: Path
) -> None:
    """load() skips empty .windsurfrules files and returns an empty list."""
    (tmp_path / ".windsurfrules").write_text("")
    skills = windsurf_adapter.load(str(tmp_path))
    assert skills == []


def test_windsurf_load_returns_empty_list_for_directory_with_no_windsurfrules(
    windsurf_adapter: WindsurfAdapter, tmp_path: Path
) -> None:
    """load() returns an empty list when no .windsurfrules files exist."""
    skills = windsurf_adapter.load(str(tmp_path))
    assert skills == []


def test_windsurf_detect_returns_true_for_directory_with_windsurfrules(
    windsurf_adapter: WindsurfAdapter,
) -> None:
    """detect() returns True for the windsurf fixtures directory."""
    assert windsurf_adapter.detect(str(WINDSURF_FIXTURES)) is True
