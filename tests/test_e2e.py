"""End-to-end tests for the full Weave load → query pipeline."""

from pathlib import Path

import pytest

from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.composer import WeaveComposer
from weave.core.registry import SkillRegistry
from weave.core.selector import WeaveSelector

CLAUDE_FIXTURES = Path(__file__).parent / "fixtures" / "claude_code"
CODEX_FIXTURES = Path(__file__).parent / "fixtures" / "codex"


@pytest.fixture(scope="module")
def registry() -> SkillRegistry:
    """Return a SkillRegistry populated from the Claude Code fixtures.

    Module-scoped so file loading and embedding run once per test session.
    """
    adapter = ClaudeCodeAdapter()
    skills = adapter.load(str(CLAUDE_FIXTURES))
    reg = SkillRegistry()
    for skill in skills:
        reg.register(skill)
    return reg


@pytest.fixture(scope="module")
def selector() -> WeaveSelector:
    """Return a WeaveSelector instance shared across all tests in this module.

    Module-scoped so the sentence-transformers model is lazy-loaded once.
    NOTE: first run downloads all-MiniLM-L6-v2 (~80MB), cached after.
    """
    return WeaveSelector()


@pytest.fixture(scope="module")
def combined_registry() -> SkillRegistry:
    """Return a registry with skills from both claude_code and codex fixtures.

    Loads both directories via ClaudeCodeAdapter — the codex fixture is a plain
    .md file, loadable without the dedicated CodexAdapter (Phase 3). Module-scoped
    so file loading runs once per test session.
    """
    adapter = ClaudeCodeAdapter()
    reg = SkillRegistry()
    for path in (CLAUDE_FIXTURES, CODEX_FIXTURES):
        for skill in adapter.load(str(path)):
            reg.register(skill)
    return reg


def test_e2e_design_query_returns_design_skill(
    selector: WeaveSelector, registry: SkillRegistry
) -> None:
    """A design query returns the Naksha Design System skill as the top result."""
    results = selector.select("design a UI component with Tailwind CSS", registry)
    assert len(results) >= 1
    assert results[0][0].name == "Naksha Design System"


def test_e2e_backend_query_returns_backend_skill(
    selector: WeaveSelector, registry: SkillRegistry
) -> None:
    """A backend query returns the Backend API Engineer skill as the top result."""
    results = selector.select(
        "build a REST API endpoint with FastAPI and PostgreSQL", registry
    )
    assert len(results) >= 1
    assert results[0][0].name == "Backend API Engineer"


def test_e2e_multi_skill_composition(
    selector: WeaveSelector, combined_registry: SkillRegistry
) -> None:
    """Multi-skill query selects two skills and composes their combined content.

    Uses confidence_threshold=1.5 to guarantee two results regardless of score
    gap, then asserts both skills' content appears in the composed output.
    Skill name appears as a heading in raw_content — reliable presence check.
    """
    results = selector.select(
        "programming", combined_registry, confidence_threshold=1.5
    )
    assert len(results) == 2

    composed = WeaveComposer().compose(results)
    assert results[0][0].name in composed
    assert results[1][0].name in composed
