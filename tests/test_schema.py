"""Tests for the universal Skill schema."""

import pytest

from weave.core.schema import Skill


@pytest.fixture
def valid_skill() -> Skill:
    """Return a fully-populated valid Skill for use in tests."""
    return Skill(
        id="test-uuid-1234",
        name="Naksha Design",
        platform="claude_code",
        source_path="/tmp/naksha.md",
        capabilities=["design", "ui", "tailwind"],
        trigger_context="UI component design and layout",
        raw_content="# Naksha\nDesign skill content",
        embedding=[0.1, 0.2, 0.3],
        metadata={"author": "Naksha Studio"},
        loaded_at="2026-04-05T10:00:00",
    )


def test_skill_creation_sets_name(valid_skill: Skill) -> None:
    """Valid skill creation sets the name field correctly."""
    assert valid_skill.name == "Naksha Design"


def test_skill_creation_sets_platform(valid_skill: Skill) -> None:
    """Valid skill creation sets the platform field correctly."""
    assert valid_skill.platform == "claude_code"


def test_skill_is_immutable(valid_skill: Skill) -> None:
    """Skill fields cannot be mutated after creation (frozen=True)."""
    with pytest.raises(Exception):
        valid_skill.name = "mutated"  # type: ignore[misc]


def test_repr_shows_name_platform_capabilities(valid_skill: Skill) -> None:
    """__repr__ includes name, platform, and capability count."""
    expected = "Skill(name='Naksha Design', platform='claude_code', capabilities=3)"
    assert repr(valid_skill) == expected


def test_to_dict_contains_all_keys(valid_skill: Skill) -> None:
    """to_dict() returns a dict with all 10 Skill field keys."""
    expected_keys = {
        "id",
        "name",
        "platform",
        "source_path",
        "capabilities",
        "trigger_context",
        "raw_content",
        "embedding",
        "metadata",
        "loaded_at",
    }
    assert set(valid_skill.to_dict().keys()) == expected_keys


def test_to_dict_values_match_original(valid_skill: Skill) -> None:
    """to_dict() values match the original Skill field values."""
    d = valid_skill.to_dict()
    assert d["name"] == valid_skill.name
    assert d["platform"] == valid_skill.platform
    assert d["embedding"] == valid_skill.embedding


def test_validate_passes_on_valid_skill(valid_skill: Skill) -> None:
    """validate() does not raise for a fully-populated valid Skill."""
    valid_skill.validate()  # must not raise


def test_validate_raises_on_empty_name(valid_skill: Skill) -> None:
    """validate() raises ValueError when name is empty."""
    skill = Skill(**{**valid_skill.to_dict(), "name": ""})
    with pytest.raises(ValueError, match="'name'"):
        skill.validate()


def test_validate_raises_on_empty_platform(valid_skill: Skill) -> None:
    """validate() raises ValueError when platform is empty."""
    skill = Skill(**{**valid_skill.to_dict(), "platform": ""})
    with pytest.raises(ValueError, match="'platform'"):
        skill.validate()


def test_validate_raises_on_empty_raw_content(valid_skill: Skill) -> None:
    """validate() raises ValueError when raw_content is empty."""
    skill = Skill(**{**valid_skill.to_dict(), "raw_content": ""})
    with pytest.raises(ValueError, match="'raw_content'"):
        skill.validate()
