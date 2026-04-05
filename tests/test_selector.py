"""Tests for the WeaveSelector skill selection engine."""

from pathlib import Path

import pytest

from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.registry import SkillRegistry
from weave.core.schema import Skill
from weave.core.selector import WeaveSelector

CLAUDE_FIXTURES = Path(__file__).parent / "fixtures" / "claude_code"


@pytest.fixture(scope="module")
def loaded_registry() -> SkillRegistry:
    """Return a SkillRegistry populated with the two real Claude Code fixtures.

    Module-scoped so file loading runs once per test session, not per test.
    Tests must not mutate this registry (no clear() or register() calls).
    """
    adapter = ClaudeCodeAdapter()
    skills = adapter.load(str(CLAUDE_FIXTURES))
    registry = SkillRegistry()
    for skill in skills:
        registry.register(skill)
    return registry


@pytest.fixture(scope="module")
def selector() -> WeaveSelector:
    """Return a WeaveSelector instance shared across all tests in this module.

    Module-scoped so the sentence-transformers model is lazy-loaded once.
    NOTE: first run downloads all-MiniLM-L6-v2 (~80MB), cached after.
    """
    return WeaveSelector()


def test_select_returns_design_skill_for_design_query(
    selector: WeaveSelector, loaded_registry: SkillRegistry
) -> None:
    """A design-focused query returns the Naksha Design System skill as top result."""
    results = selector.select(
        "design a UI component with Tailwind CSS", loaded_registry
    )
    assert results[0][0].name == "Naksha Design System"


def test_select_returns_two_skills_when_scores_are_close(
    selector: WeaveSelector, loaded_registry: SkillRegistry
) -> None:
    """select() returns two skills when confidence_threshold exceeds the score gap."""
    results = selector.select(
        "programming",
        loaded_registry,
        confidence_threshold=1.5,
    )
    assert len(results) == 2


def test_select_returns_empty_list_when_registry_is_empty(
    selector: WeaveSelector,
) -> None:
    """select() returns an empty list when the registry contains no skills."""
    empty_registry = SkillRegistry()
    results = selector.select("any query", empty_registry)
    assert results == []


def test_select_explain_flag_does_not_crash(
    selector: WeaveSelector, loaded_registry: SkillRegistry
) -> None:
    """select() with explain=True completes without raising an exception."""
    selector.select("design a component", loaded_registry, explain=True)
    assert True


@pytest.fixture
def two_skill_registry() -> SkillRegistry:
    """Return a SkillRegistry with two named skills and empty embeddings."""
    registry = SkillRegistry()
    for name, platform in [("Alpha Skill", "claude_code"), ("Beta Skill", "cursor")]:
        registry.register(
            Skill(
                id=f"id-{name}",
                name=name,
                platform=platform,
                source_path=f"/tmp/{name}.md",
                capabilities=["testing"],
                trigger_context=f"Trigger for {name}",
                raw_content=f"# {name}",
                embedding=[],
                metadata={},
                loaded_at="2026-04-05T10:00:00+00:00",
            )
        )
    return registry


def test_select_all_returns_all_skills(
    selector: WeaveSelector, two_skill_registry: SkillRegistry
) -> None:
    """select_all() returns all skills in the registry."""
    results = selector.select_all(two_skill_registry, max_active_skills=10)
    assert len(results) == 2


def test_select_all_respects_max_active_skills(
    selector: WeaveSelector, two_skill_registry: SkillRegistry
) -> None:
    """select_all() caps results at max_active_skills."""
    results = selector.select_all(two_skill_registry, max_active_skills=1)
    assert len(results) == 1


def test_select_manual_returns_named_skills(
    selector: WeaveSelector, two_skill_registry: SkillRegistry
) -> None:
    """select_manual() returns skills whose names are in the names list."""
    results = selector.select_manual(["Alpha Skill"], two_skill_registry)
    assert len(results) == 1
    assert results[0][0].name == "Alpha Skill"
    assert results[0][1] == 1.0


def test_select_manual_skips_unknown_names(
    selector: WeaveSelector, two_skill_registry: SkillRegistry
) -> None:
    """select_manual() returns empty list when no names match any registered skill."""
    results = selector.select_manual(["Nonexistent Skill"], two_skill_registry)
    assert results == []
