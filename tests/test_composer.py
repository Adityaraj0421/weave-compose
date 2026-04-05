"""Tests for the WeaveComposer multi-skill context merger."""

import pytest

from weave.core.composer import WeaveComposer
from weave.core.schema import Skill


@pytest.fixture
def composer() -> WeaveComposer:
    """Return a fresh WeaveComposer for each test."""
    return WeaveComposer()


@pytest.fixture
def skill_a() -> Skill:
    """Higher-score design skill with known raw_content and a shared line."""
    return Skill(
        id="skill-a-001",
        name="Design Skill",
        platform="claude_code",
        source_path="/tmp/design.md",
        capabilities=["design", "ui"],
        trigger_context="Handles UI component design and Tailwind CSS.",
        raw_content="# Design Skill\nUse Tailwind for all styling.\nShared rule: always lint.",
        embedding=[],
        metadata={},
        loaded_at="2026-04-05T10:00:00+00:00",
    )


@pytest.fixture
def skill_b() -> Skill:
    """Lower-score backend skill with known raw_content and a shared line."""
    return Skill(
        id="skill-b-002",
        name="Backend Skill",
        platform="claude_code",
        source_path="/tmp/backend.md",
        capabilities=["api", "backend"],
        trigger_context="Handles REST API design with FastAPI.",
        raw_content="# Backend Skill\nUse FastAPI for all endpoints.\nShared rule: always lint.",
        embedding=[],
        metadata={},
        loaded_at="2026-04-05T10:00:00+00:00",
    )


def test_compose_single_skill_returns_raw_content(
    composer: WeaveComposer, skill_a: Skill
) -> None:
    """compose() with one skill returns its raw_content stripped, unchanged."""
    result = composer.compose([(skill_a, 0.9)])
    assert result == skill_a.raw_content.strip()


def test_compose_two_skills_both_present_in_output(
    composer: WeaveComposer, skill_a: Skill, skill_b: Skill
) -> None:
    """compose() with two skills contains content from both."""
    result = composer.compose([(skill_a, 0.9), (skill_b, 0.5)])
    assert "Use Tailwind for all styling." in result
    assert "Use FastAPI for all endpoints." in result


def test_compose_duplicate_lines_appear_only_once(
    composer: WeaveComposer, skill_a: Skill, skill_b: Skill
) -> None:
    """compose() removes lines that appear in both skills' raw_content."""
    result = composer.compose([(skill_a, 0.9), (skill_b, 0.5)])
    assert result.count("Shared rule: always lint.") == 1


def test_compose_higher_score_skill_appears_first(
    composer: WeaveComposer, skill_a: Skill, skill_b: Skill
) -> None:
    """compose() places the higher-score skill's content before lower-score."""
    result = composer.compose([(skill_b, 0.5), (skill_a, 0.9)])
    assert result.index("Use Tailwind for all styling.") < result.index(
        "Use FastAPI for all endpoints."
    )


def test_compose_minimal_is_shorter_than_compose(
    composer: WeaveComposer, skill_a: Skill, skill_b: Skill
) -> None:
    """compose_minimal() output is strictly shorter than compose() for same input."""
    skills = [(skill_a, 0.9), (skill_b, 0.5)]
    assert len(composer.compose_minimal(skills)) < len(composer.compose(skills))


def test_compose_empty_skills_returns_empty_string(
    composer: WeaveComposer,
) -> None:
    """compose() and compose_minimal() both return '' for empty input."""
    assert composer.compose([]) == ""
    assert composer.compose_minimal([]) == ""


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_detect_conflicts_returns_empty_for_non_conflicting_skills(
    composer: WeaveComposer,
    skill_a: Skill,
    skill_b: Skill,
) -> None:
    """detect_conflicts() returns [] when skills have no opposing keywords."""
    # skill_a and skill_b fixtures have different domains, no opposing keywords
    skill_a_emb = Skill(
        id=skill_a.id, name=skill_a.name, platform=skill_a.platform,
        source_path=skill_a.source_path, capabilities=skill_a.capabilities,
        trigger_context=skill_a.trigger_context, raw_content=skill_a.raw_content,
        embedding=[0.1, 0.2, 0.3], metadata=skill_a.metadata, loaded_at=skill_a.loaded_at,
    )
    skill_b_emb = Skill(
        id=skill_b.id, name=skill_b.name, platform=skill_b.platform,
        source_path=skill_b.source_path, capabilities=skill_b.capabilities,
        trigger_context=skill_b.trigger_context, raw_content=skill_b.raw_content,
        embedding=[0.9, 0.8, 0.7], metadata=skill_b.metadata, loaded_at=skill_b.loaded_at,
    )
    result = composer.detect_conflicts([(skill_a_emb, 0.9), (skill_b_emb, 0.5)])
    assert result == []


def test_detect_conflicts_returns_empty_when_embeddings_absent(
    composer: WeaveComposer,
) -> None:
    """detect_conflicts() returns [] when embeddings are empty (cannot compare)."""
    skill_tabs = Skill(
        id="conf-001", name="Tabs Skill", platform="claude_code",
        source_path="/tmp/tabs.md", capabilities=["style"],
        trigger_context="formatting", raw_content="always use tabs for indentation",
        embedding=[], metadata={}, loaded_at="2026-04-05T10:00:00+00:00",
    )
    skill_spaces = Skill(
        id="conf-002", name="Spaces Skill", platform="claude_code",
        source_path="/tmp/spaces.md", capabilities=["style"],
        trigger_context="formatting", raw_content="never use tabs, always use spaces",
        embedding=[], metadata={}, loaded_at="2026-04-05T10:00:00+00:00",
    )
    result = composer.detect_conflicts([(skill_tabs, 0.9), (skill_spaces, 0.8)])
    assert result == []


def test_detect_conflicts_detects_opposing_keyword_conflict(
    composer: WeaveComposer,
) -> None:
    """detect_conflicts() returns a pair when sim >= threshold and keywords oppose."""
    shared_vec = [1.0, 0.0, 0.0]  # identical embedding → sim == 1.0
    skill_tabs = Skill(
        id="conf-003", name="Tabs Skill", platform="claude_code",
        source_path="/tmp/tabs.md", capabilities=["style"],
        trigger_context="code formatting style",
        raw_content="always use tabs for indentation in all files",
        embedding=shared_vec, metadata={}, loaded_at="2026-04-05T10:00:00+00:00",
    )
    skill_spaces = Skill(
        id="conf-004", name="Spaces Skill", platform="claude_code",
        source_path="/tmp/spaces.md", capabilities=["style"],
        trigger_context="code formatting style",
        raw_content="never use tabs, avoid tabs completely, use spaces only",
        embedding=shared_vec, metadata={}, loaded_at="2026-04-05T10:00:00+00:00",
    )
    result = composer.detect_conflicts([(skill_tabs, 0.9), (skill_spaces, 0.8)])
    assert len(result) == 1
    assert result[0][0].name == "Tabs Skill"
    assert result[0][1].name == "Spaces Skill"
