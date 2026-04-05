"""Tests for the SkillRegistry in-memory store."""

import json
from pathlib import Path

import pytest

from weave.core.registry import SkillRegistry
from weave.core.schema import Skill


@pytest.fixture
def registry() -> SkillRegistry:
    """Return a fresh empty SkillRegistry for each test."""
    return SkillRegistry()


@pytest.fixture
def skill() -> Skill:
    """Return a fully-populated Skill with a known embedding for round-trip tests."""
    return Skill(
        id="test-id-001",
        name="Test Skill",
        platform="claude_code",
        source_path="/tmp/test.md",
        capabilities=["testing", "registry"],
        trigger_context="Test trigger context for registry tests",
        raw_content="# Test Skill\nContent here.",
        embedding=[0.1, 0.2, 0.3],
        metadata={"author": "Test Author"},
        loaded_at="2026-04-05T10:00:00+00:00",
    )


def test_register_and_retrieve_by_id(registry: SkillRegistry, skill: Skill) -> None:
    """register() stores the skill and get_by_id() returns the same object."""
    registry.register(skill)
    assert registry.get_by_id(skill.id) == skill


def test_get_by_platform_filters_correctly(registry: SkillRegistry, skill: Skill) -> None:
    """get_by_platform() returns only skills matching the given platform string."""
    cursor_skill = Skill(**{**skill.to_dict(), "id": "cursor-002", "platform": "cursor"})
    registry.register(skill)
    registry.register(cursor_skill)
    results = registry.get_by_platform("claude_code")
    assert len(results) == 1
    assert results[0].platform == "claude_code"


def test_clear_empties_registry(registry: SkillRegistry, skill: Skill) -> None:
    """clear() removes all skills so count() returns 0."""
    registry.register(skill)
    registry.clear()
    assert registry.count() == 0


def test_count_returns_correct_number(registry: SkillRegistry, skill: Skill) -> None:
    """count() reflects the number of distinct skills registered."""
    second = Skill(**{**skill.to_dict(), "id": "test-id-002"})
    registry.register(skill)
    registry.register(second)
    assert registry.count() == 2


def test_duplicate_id_overwrites(registry: SkillRegistry, skill: Skill) -> None:
    """Registering a skill with a duplicate id overwrites the previous entry."""
    updated = Skill(**{**skill.to_dict(), "name": "Updated Name"})
    registry.register(skill)
    registry.register(updated)
    result = registry.get_by_id(skill.id)
    assert result is not None
    assert result.name == "Updated Name"


def test_save_session_writes_valid_json_file(
    registry: SkillRegistry, skill: Skill, tmp_path: Path
) -> None:
    """save_session() writes a valid JSON file with version and skills list."""
    session_path = tmp_path / "session.json"
    registry.register(skill)
    registry.save_session(str(session_path))
    assert session_path.exists()
    data = json.loads(session_path.read_text())
    assert data["version"] == "1"
    assert len(data["skills"]) == 1


def test_load_session_restores_skills_including_embeddings(
    registry: SkillRegistry, skill: Skill, tmp_path: Path
) -> None:
    """load_session() restores all skills including float embedding values."""
    session_path = str(tmp_path / "session.json")
    registry.register(skill)
    registry.save_session(session_path)

    fresh = SkillRegistry()
    fresh.load_session(session_path)
    restored = fresh.get_all()[0]
    assert restored.embedding == [0.1, 0.2, 0.3]


def test_load_session_on_missing_file_leaves_registry_empty(
    registry: SkillRegistry,
) -> None:
    """load_session() on a non-existent path logs a warning and does not raise."""
    registry.load_session("/nonexistent/path/weave_session.json")
    assert registry.count() == 0
