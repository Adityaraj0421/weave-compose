"""Tests for the WeaveSelector skill selection engine."""

from pathlib import Path

import pytest

from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.registry import SkillRegistry
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
