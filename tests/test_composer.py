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
