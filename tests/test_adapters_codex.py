"""Tests for the CodexAdapter."""

from pathlib import Path

import pytest

from weave.core.adapters.codex import CodexAdapter

CODEX_FIXTURES = Path(__file__).parent / "fixtures" / "codex"


@pytest.fixture
def codex_adapter() -> CodexAdapter:
    """Return a fresh CodexAdapter instance for each test."""
    return CodexAdapter()


def test_codex_load_returns_all_skills_from_directory(
    codex_adapter: CodexAdapter,
) -> None:
    """load() returns one Skill per codex file found (AGENTS.md + .codex/*.md)."""
    skills = codex_adapter.load(str(CODEX_FIXTURES))
    assert len(skills) == 2


def test_codex_load_parses_agents_md_heading_name(codex_adapter: CodexAdapter) -> None:
    """load() uses the first # heading as name for AGENTS.md files."""
    skills = codex_adapter.load(str(CODEX_FIXTURES))
    names = {s.name for s in skills}
    assert "Security Code Reviewer" in names


def test_codex_load_parses_first_paragraph_as_trigger_context(
    codex_adapter: CodexAdapter,
) -> None:
    """load() uses the first non-heading paragraph as trigger_context."""
    skills = codex_adapter.load(str(CODEX_FIXTURES))
    agents_skill = next(s for s in skills if s.name == "Security Code Reviewer")
    assert "security" in agents_skill.trigger_context.lower()


def test_codex_load_handles_empty_file_without_crashing(
    codex_adapter: CodexAdapter, tmp_path: Path
) -> None:
    """load() skips an empty AGENTS.md and returns an empty list."""
    (tmp_path / "AGENTS.md").write_text("")
    skills = codex_adapter.load(str(tmp_path))
    assert skills == []


def test_codex_load_returns_empty_list_for_directory_with_no_codex_files(
    codex_adapter: CodexAdapter, tmp_path: Path
) -> None:
    """load() returns an empty list when no AGENTS.md or .codex/*.md files exist."""
    skills = codex_adapter.load(str(tmp_path))
    assert skills == []


def test_codex_detect_returns_true_for_directory_with_agents_md(
    codex_adapter: CodexAdapter,
) -> None:
    """detect() returns True for the codex fixtures directory."""
    assert codex_adapter.detect(str(CODEX_FIXTURES)) is True


# ---------------------------------------------------------------------------
# Manifest (weave.skill.json) tests — CodexAdapter
# ---------------------------------------------------------------------------

def test_codex_adapter_applies_manifest(
    codex_adapter: CodexAdapter,
) -> None:
    """load() applies weave.skill.json manifest to codex skills."""
    skills = codex_adapter.load(str(CODEX_FIXTURES))
    manifest_skill = next(
        (s for s in skills if s.metadata.get("version") == "1.1.0"), None
    )
    assert manifest_skill is not None
    assert manifest_skill.name == "Security Code Reviewer"
